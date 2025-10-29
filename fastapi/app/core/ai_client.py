# app/core/ai_client.py
import requests
import json
import os
from typing import Optional, Dict, Any
from app.core.config import settings


class AIClient:
    """AI客户端，基于你提供的AI调用代码"""

    def __init__(self, api_url: str = None, api_key: str = None):
        # 使用传入参数或默认配置
        self.api_url = api_url or "http://erp.miraclink.com:5200/v1/chat-messages"
        self.upload_url = api_url.replace("chat-messages",
                                          "files/upload") if api_url else "http://erp.miraclink.com:5200/v1/files/upload"
        self.api_key = api_key or "app-r2VTsPlXK2kQDSVtz2zCdBNJ"
        self.user_id = "system-md-editor"  # 系统用户ID

    def chat_with_ai(self, query: str, file_ids: Optional[list] = None, file_types: Optional[list] = None) -> Optional[
        str]:
        """
        与AI对话，基于你的原始代码改造
        """
        # 准备请求数据
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "conversation_id": "",
            "user": self.user_id,
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

        try:
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30  # 添加超时
            )

            # 处理响应
            if response.status_code == 200:
                response_data = response.json()
                answer = response_data.get("answer", "")
                return answer
            else:
                print(f"AI请求失败，状态码: {response.status_code}")
                print("错误信息:", response.text)
                return None

        except Exception as e:
            print(f"AI请求异常: {e}")
            return None

    def optimize_markdown(self, content: str, optimization_type: str = "general") -> Optional[str]:
        """
        优化Markdown内容
        """
        # 根据优化类型构建不同的提示词
        prompts = {
            "general": """请优化以下Markdown文档，要求：
        1. 保持原有结构和格式不变
        2. 提升表达质量、逻辑清晰度和可读性
        3. 保持文字内容长度基本一致，不做大幅增减
        4. 保留所有原有信息，仅优化表达方式
        请处理以下内容：""",

            "grammar": """请检查并修正以下Markdown文档，要求：
        1. 修正语法错误、拼写错误和标点符号问题
        2. 保持原有Markdown格式和结构完全不变
        3. 保持文字内容长度基本一致
        4. 仅进行错误修正，不改变原意和表达风格
        请处理以下内容：""",

            "structure": """请优化以下Markdown文档的结构和层次，要求：
        1. 调整标题层级、段落组织和内容排列
        2. 使文档结构更加清晰有序和逻辑性强
        3. 保持原有内容完整，文字长度基本不变
        4. 可调整内容顺序，但不删减或大幅增加内容
        请处理以下内容：""",

            "expand": """请适度扩展以下Markdown文档的内容，要求：
        1. 保持原有Markdown结构和格式
        2. 在现有内容基础上适当补充细节和说明
        3. 扩展幅度控制在原文的1.2-1.5倍长度范围内
        4. 确保扩展内容与原文风格一致，逻辑连贯
        5. 重点补充实用性强的信息，避免冗余内容
        请处理以下内容："""
        }

        prompt = prompts.get(optimization_type, prompts["general"])
        query = f"{prompt}\n\n{content}"

        return self.chat_with_ai(query)


# 创建默认AI客户端实例
default_ai_client = AIClient()