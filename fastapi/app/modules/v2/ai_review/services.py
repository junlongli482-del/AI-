import requests
import json
import os
import time
import mimetypes
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
import PyPDF2

from app.core.database import get_db
from app.modules.v2.ai_review.models import AIReviewLog, ReviewRule
from app.modules.v2.ai_review.schemas import ReviewType, ReviewResult, ReviewLogResponse, ReviewStatusResponse, \
    ReviewStatsResponse
from app.modules.v2.document_manager.models import Document


class AIReviewService:
    def __init__(self):
        # AI服务配置 - 更新API密钥
        self.api_url = "http://erp.miraclink.com:5200/v1/chat-messages"
        self.upload_url = "http://erp.miraclink.com:5200/v1/files/upload"
        self.api_key = "app-szggphzO1DQGrBx3ISQp0iEY"  # 更新的API密钥

        # 由于AI服务端已经预设了审核提示词，这里只保留一个说明
        self.review_prompt_info = """审核内容如下
"""

    def review_content_directly(self, title: str, content: str, document_id: Optional[int] = None) -> Dict[str, Any]:
        """
        直接审核文档内容，不保存到数据库

        Args:
            title: 文档标题
            content: 文档内容
            document_id: 文档ID（可选，用于日志记录）

        Returns:
            Dict: 审核结果
        """
        start_time = time.time()

        try:
            print(f"开始直接内容审核，标题: {title[:50]}...")
            print(f"内容长度: {len(content)} 字符")
            if document_id:
                print(f"关联文档ID: {document_id}")

            # 第一步：检查内容长度限制（MD格式，最多1000行）
            print("第一步：检查内容长度限制...")
            size_passed, size_failure_reason, line_count = self.check_md_lines(content)

            if not size_passed:
                print(f"❌ 内容长度检查未通过: {size_failure_reason}")
                review_duration = time.time() - start_time
                return {
                    "success": True,
                    "review_result": "failed",
                    "review_message": "内容审核未通过",
                    "failure_reason": size_failure_reason,
                    "review_duration": round(review_duration, 2)
                }

            print(f"✅ 内容长度检查通过（{line_count}行），开始AI内容安全审核...")

            # 第二步：AI内容安全审核
            # 构建审核内容（标题 + 内容）
            review_content = f"标题：{title}\n\n内容：\n{content}"

            # 调用AI服务进行内容安全审核
            ai_response = self.chat_with_ai(review_content, user_id="content_review")

            if ai_response:
                # 解析AI响应
                passed, failure_reason = self.parse_ai_response(ai_response)
                review_duration = time.time() - start_time

                if passed:
                    print("✅ AI内容安全审核通过")
                    return {
                        "success": True,
                        "review_result": "passed",
                        "review_message": "内容审核通过",
                        "failure_reason": None,
                        "review_duration": round(review_duration, 2)
                    }
                else:
                    print(f"❌ AI内容安全审核未通过: {failure_reason}")
                    return {
                        "success": True,
                        "review_result": "failed",
                        "review_message": "内容审核未通过",
                        "failure_reason": failure_reason,
                        "review_duration": round(review_duration, 2)
                    }
            else:
                print("❌ AI服务调用失败")
                review_duration = time.time() - start_time
                return {
                    "success": False,
                    "review_result": "failed",
                    "review_message": "审核服务异常",
                    "failure_reason": "AI服务调用失败，请稍后重试",
                    "review_duration": round(review_duration, 2)
                }

        except Exception as e:
            print(f"❌ 内容审核异常: {str(e)}")
            review_duration = time.time() - start_time
            return {
                "success": False,
                "review_result": "failed",
                "review_message": "审核过程异常",
                "failure_reason": f"审核异常: {str(e)}",
                "review_duration": round(review_duration, 2)
            }


    def get_file_type(self, filename: str) -> str:
        """根据文件扩展名确定文件类型"""
        extension = os.path.splitext(filename)[1].lower().replace('.', '')

        # 文档类型
        document_extensions = ['txt', 'md', 'markdown', 'pdf', 'html', 'xlsx', 'xls', 'docx', 'csv', 'eml', 'msg',
                               'pptx',
                               'ppt', 'xml', 'epub']
        # 图片类型
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
        # 音频类型
        audio_extensions = ['mp3', 'm4a', 'wav', 'webm', 'amr']
        # 视频类型
        video_extensions = ['mp4', 'mov', 'mpeg', 'mpga']

        if extension in document_extensions:
            return 'document'
        elif extension in image_extensions:
            return 'image'
        elif extension in audio_extensions:
            return 'audio'
        elif extension in video_extensions:
            return 'video'
        else:
            return 'custom'

    def check_pdf_pages(self, file_path: str) -> Tuple[bool, Optional[str], int]:
        """检查PDF文件页数"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)

                if page_count > 10:
                    return False, f"PDF文件共{page_count}页，超过10页限制", page_count
                else:
                    return True, None, page_count

        except Exception as e:
            return False, f"PDF文件检查失败: {str(e)}", 0

    def check_md_lines(self, content: str) -> Tuple[bool, Optional[str], int]:
        """检查MD文档行数"""
        try:
            lines = content.split('\n')
            line_count = len(lines)

            if line_count > 1000:
                return False, f"MD文档共{line_count}行，超过1000行限制", line_count
            else:
                return True, None, line_count

        except Exception as e:
            return False, f"MD文档检查失败: {str(e)}", 0

    def check_document_size_limit(self, document: Document) -> Tuple[bool, Optional[str]]:
        """检查文档大小限制（本地检查）"""
        try:
            if document.file_type == 'pdf':
                if not document.file_path or not os.path.exists(document.file_path):
                    return False, "PDF文件路径不存在"

                passed, failure_reason, page_count = self.check_pdf_pages(document.file_path)
                print(f"PDF文件检查: {page_count}页, 结果: {'通过' if passed else failure_reason}")
                return passed, failure_reason

            elif document.file_type == 'md':
                if not document.content:
                    return False, "MD文档内容为空"

                passed, failure_reason, line_count = self.check_md_lines(document.content)
                print(f"MD文档检查: {line_count}行, 结果: {'通过' if passed else failure_reason}")
                return passed, failure_reason

            return True, None

        except Exception as e:
            return False, f"文档大小检查异常: {str(e)}"

    def upload_file_to_ai(self, file_path: str, user_id: str) -> Optional[str]:
        """上传文件到AI服务"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        try:
            filename = os.path.basename(file_path)
            file_type = self.get_file_type(filename)

            # 获取文件的MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            # 准备上传文件
            files = {
                'file': (filename, open(file_path, 'rb'), mime_type)
            }
            data = {
                'user': user_id
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            print(f"正在上传文件到AI服务: {file_path}")

            response = requests.post(
                self.upload_url,
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )

            if response.status_code in [200, 201]:
                upload_data = response.json()
                file_id = upload_data.get("id")
                print(f"✅ 文件上传成功! 文件ID: {file_id}")
                return file_id
            else:
                print(f"❌ 文件上传失败，状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return None

        except Exception as e:
            print(f"上传文件时发生错误: {e}")
            return None
        finally:
            if 'files' in locals() and files['file'][1]:
                files['file'][1].close()

    def chat_with_ai(self, query: str, file_ids: List[str] = None, file_types: List[str] = None,
                     user_id: str = "default") -> Optional[str]:
        """与AI对话，AI服务端已预设审核提示词"""
        try:
            # 准备请求数据
            payload = {
                "inputs": {},
                "query": query,  # 直接发送要审核的内容，不需要额外的提示词
                "response_mode": "blocking",
                "conversation_id": "",
                "user": user_id,
                "files": []
            }

            # 如果有文件ID，添加到files数组中
            if file_ids and file_types:
                for file_id, file_type in zip(file_ids, file_types):
                    payload["files"].append({
                        "type": file_type,
                        "transfer_method": "local_file",
                        "upload_file_id": file_id
                    })

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            print(f"📤 发送内容安全审核请求到AI...")
            print(f"查询内容长度: {len(query)} 字符")
            if file_ids:
                print(f"使用文件ID: {file_ids}")

            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=120  # 增加超时时间到2分钟
            )

            # 处理响应
            if response.status_code == 200:
                print("✅ AI内容安全审核请求成功！")
                response_data = response.json()
                answer = response_data.get("answer", "")
                print(f"🤖 AI审核回复: {answer[:200]}...")

                # 记录完整的AI响应用于调试
                print(f"📊 AI服务耗时: {response_data.get('metadata', {}).get('usage', {}).get('latency', 0):.2f}秒")

                return answer
            else:
                print(f"❌ AI审核请求失败，状态码: {response.status_code}")
                print("错误信息:", response.text)
                return None

        except Exception as e:
            print(f"AI审核请求异常: {e}")
            return None

    def parse_ai_response(self, ai_response: str) -> Tuple[bool, Optional[str]]:
        """解析AI审核响应"""
        if not ai_response:
            return False, "AI服务无响应"

        lines = ai_response.strip().split('\n')
        if not lines:
            return False, "AI响应格式错误"

        first_line = lines[0].strip().lower()

        if first_line == 'true':
            return True, None
        elif first_line == 'false':
            # 获取失败原因
            if len(lines) > 1:
                failure_reason = '\n'.join(lines[1:]).strip()
                return False, failure_reason
            else:
                return False, "内容审核未通过，但未提供具体原因"
        else:
            # 处理AI可能返回的其他格式
            if 'true' in first_line.lower():
                return True, None
            elif 'false' in first_line.lower():
                return False, "内容审核未通过"
            else:
                return False, f"AI响应格式不符合预期: {first_line}"

    def perform_document_review(self, document: Document, user_id: int, db: Session) -> AIReviewLog:
        """执行文档审核（先检查大小，再进行AI内容安全审核）"""
        start_time = time.time()

        # 创建审核日志记录
        review_log = AIReviewLog(
            document_id=document.id,
            user_id=user_id,
            review_type='content_safety',
            ai_provider='default',
            review_prompt=self.review_prompt_info,  # 记录提示词信息
            review_result='pending'
        )

        try:
            print(f"开始审核文档 ID: {document.id}")

            # 第一步：检查文档大小限制
            print("第一步：检查文档大小限制...")
            size_passed, size_failure_reason = self.check_document_size_limit(document)

            if not size_passed:
                print(f"❌ 文档大小检查未通过: {size_failure_reason}")
                review_log.review_result = 'failed'
                review_log.failure_reason = size_failure_reason
                review_log.ai_response = f"大小检查结果: {size_failure_reason}"
            else:
                print("✅ 文档大小检查通过，开始AI内容安全审核...")

                # 第二步：AI内容安全审核
                file_id = None
                file_types = []

                # 如果是PDF文件，需要上传到AI服务
                if document.file_type == 'pdf' and document.file_path:
                    file_id = self.upload_file_to_ai(document.file_path, f"user_{user_id}")
                    if file_id:
                        review_log.file_id = file_id
                        file_types = ['document']

                # 准备审核内容 - 不需要额外的提示词，AI服务端已预设
                if document.file_type == 'md' and document.content:
                    # MD文件直接发送内容，AI服务端会用预设的提示词进行审核
                    ai_response = self.chat_with_ai(document.content, user_id=f"user_{user_id}")
                elif file_id:
                    # PDF文件使用上传的文件ID，发送一个简单的审核请求
                    ai_response = self.chat_with_ai("请审核这个文档的内容安全性", [file_id], file_types,
                                                    f"user_{user_id}")
                else:
                    ai_response = None

                review_log.ai_response = ai_response

                if ai_response:
                    passed, failure_reason = self.parse_ai_response(ai_response)
                    review_log.review_result = 'passed' if passed else 'failed'
                    review_log.failure_reason = failure_reason
                    print(f"AI内容安全审核结果: {'通过' if passed else '未通过'}")
                    if failure_reason:
                        print(f"失败原因: {failure_reason}")
                else:
                    review_log.review_result = 'error'
                    review_log.failure_reason = "AI服务调用失败"
                    print("❌ AI服务调用失败")

            # 计算审核耗时
            review_log.review_duration = int(time.time() - start_time)

        except Exception as e:
            print(f"❌ 审核异常: {str(e)}")
            review_log.review_result = 'error'
            review_log.failure_reason = f"审核异常: {str(e)}"
            review_log.review_duration = int(time.time() - start_time)

        # 保存审核日志
        db.add(review_log)
        db.commit()
        db.refresh(review_log)

        return review_log

    def submit_document_review(self, document: Document, user_id: int, db: Session) -> AIReviewLog:
        """提交文档审核"""
        print(f"提交文档审核，文档ID: {document.id}, 类型: {document.file_type}")

        # 执行审核
        review_log = self.perform_document_review(document, user_id, db)

        # 更新文档状态
        self.update_document_status(document, review_log, db)

        return review_log

    def update_document_status(self, document: Document, review_log: AIReviewLog, db: Session):
        """根据审核结果更新文档状态"""
        if review_log.review_result == 'passed':
            document.status = 'published'
            document.publish_time = datetime.now()
            document.review_message = "内容安全审核通过"
            print(f"✅ 文档状态更新为: published")
        elif review_log.review_result == 'failed':
            document.status = 'review_failed'
            document.review_message = f"审核未通过：{review_log.failure_reason}"
            print(f"❌ 文档状态更新为: review_failed")
        elif review_log.review_result == 'error':
            document.status = 'review_failed'
            document.review_message = "审核过程中出现错误，请重新提交"
            print(f"⚠️ 文档状态更新为: review_failed (错误)")

        db.commit()

    # 其他方法保持不变...
    def get_review_status(self, document_id: int, user_id: int, db: Session) -> ReviewStatusResponse:
        """获取文档审核状态"""
        # 获取最新的审核日志
        review_log = db.query(AIReviewLog).filter(
            and_(
                AIReviewLog.document_id == document_id,
                AIReviewLog.user_id == user_id
            )
        ).order_by(desc(AIReviewLog.created_at)).first()

        if not review_log:
            return ReviewStatusResponse(
                document_id=document_id,
                overall_status=ReviewResult.pending,
                review_logs=[],
                total_reviews=0,
                passed_reviews=0,
                failed_reviews=0,
                pending_reviews=1
            )

        # 统计审核结果
        review_logs = [review_log]
        total_reviews = 1
        passed_reviews = 1 if review_log.review_result == 'passed' else 0
        failed_reviews = 1 if review_log.review_result == 'failed' else 0
        pending_reviews = 1 if review_log.review_result == 'pending' else 0

        return ReviewStatusResponse(
            document_id=document_id,
            overall_status=ReviewResult(review_log.review_result),
            review_logs=[ReviewLogResponse.from_orm(review_log)],
            total_reviews=total_reviews,
            passed_reviews=passed_reviews,
            failed_reviews=failed_reviews,
            pending_reviews=pending_reviews
        )

    def get_review_history(self, user_id: int, page: int, size: int, review_result: Optional[ReviewResult],
                           db: Session) -> Dict[str, Any]:
        """获取审核历史"""
        query = db.query(AIReviewLog).filter(AIReviewLog.user_id == user_id)

        if review_result:
            query = query.filter(AIReviewLog.review_result == review_result)

        # 分页
        total = query.count()
        review_logs = query.order_by(desc(AIReviewLog.created_at)).offset((page - 1) * size).limit(size).all()

        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "items": [ReviewLogResponse.from_orm(log) for log in review_logs]
        }

    def get_review_stats(self, user_id: int, db: Session) -> ReviewStatsResponse:
        """获取审核统计信息"""
        # 总审核数
        total_reviews = db.query(AIReviewLog).filter(AIReviewLog.user_id == user_id).count()

        # 今日审核数
        today = datetime.now().date()
        today_reviews = db.query(AIReviewLog).filter(
            and_(
                AIReviewLog.user_id == user_id,
                func.date(AIReviewLog.created_at) == today
            )
        ).count()

        # 通过率和失败率
        if total_reviews > 0:
            passed_count = db.query(AIReviewLog).filter(
                and_(
                    AIReviewLog.user_id == user_id,
                    AIReviewLog.review_result == 'passed'
                )
            ).count()
            failed_count = db.query(AIReviewLog).filter(
                and_(
                    AIReviewLog.user_id == user_id,
                    AIReviewLog.review_result == 'failed'
                )
            ).count()

            passed_rate = passed_count / total_reviews
            failed_rate = failed_count / total_reviews
        else:
            passed_rate = 0.0
            failed_rate = 0.0

        # 平均审核时长 - 修复格式化问题
        avg_duration_result = db.query(func.avg(AIReviewLog.review_duration)).filter(
            and_(
                AIReviewLog.user_id == user_id,
                AIReviewLog.review_duration.isnot(None)
            )
        ).scalar()

        # 确保返回值不是None
        avg_review_duration = float(avg_duration_result) if avg_duration_result is not None else 0.0

        # 审核类型统计（只有content_safety）
        review_type_stats = {
            "content_safety": total_reviews
        }

        # 最近审核记录
        recent_reviews = db.query(AIReviewLog).filter(
            AIReviewLog.user_id == user_id
        ).order_by(desc(AIReviewLog.created_at)).limit(5).all()

        return ReviewStatsResponse(
            total_reviews=total_reviews,
            today_reviews=today_reviews,
            passed_rate=passed_rate,
            failed_rate=failed_rate,
            avg_review_duration=avg_review_duration,
            review_type_stats=review_type_stats,
            recent_reviews=[ReviewLogResponse.from_orm(log) for log in recent_reviews]
        )


# 创建全局服务实例
ai_review_service = AIReviewService()