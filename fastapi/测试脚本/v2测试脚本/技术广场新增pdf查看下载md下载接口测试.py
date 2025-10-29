"""
技术广场文件访问功能测试脚本
测试无需认证的文件下载、预览、流式传输功能
"""
import requests
import json
import os
from pathlib import Path
import time


class TechSquareFileTest:
    def __init__(self, base_url="http://localhost:8100"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v2/tech_square"
        self.test_results = []

    def log_test(self, test_name, success, message, response_data=None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if response_data:
            result["data"] = response_data

        self.test_results.append(result)

        # 控制台输出
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   响应数据: {response_data}")
        print()

    def test_module_health(self):
        """测试模块健康检查"""
        try:
            response = requests.get(f"{self.api_base}/test")

            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "模块健康检查",
                    True,
                    f"模块运行正常 - {data.get('message', '')}"
                )
                return True
            else:
                self.log_test(
                    "模块健康检查",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False

        except Exception as e:
            self.log_test("模块健康检查", False, f"请求异常: {str(e)}")
            return False

    def get_published_documents(self):
        """获取已发布文档列表"""
        try:
            response = requests.get(f"{self.api_base}/documents?page=1&size=5")

            if response.status_code == 200:
                data = response.json()
                documents = data.get('documents', [])

                if documents:
                    self.log_test(
                        "获取已发布文档",
                        True,
                        f"找到 {len(documents)} 个已发布文档"
                    )
                    return documents
                else:
                    self.log_test(
                        "获取已发布文档",
                        False,
                        "没有找到已发布的文档，请先发布一些文档"
                    )
                    return []
            else:
                self.log_test(
                    "获取已发布文档",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return []

        except Exception as e:
            self.log_test("获取已发布文档", False, f"请求异常: {str(e)}")
            return []

    def test_file_info(self, document_id):
        """测试获取文件信息接口"""
        try:
            response = requests.get(f"{self.api_base}/documents/{document_id}/info")

            if response.status_code == 200:
                data = response.json()

                # 验证响应字段
                required_fields = [
                    'document_id', 'title', 'file_type', 'file_size',
                    'has_file', 'safe_filename', 'file_exists'
                ]

                missing_fields = [field for field in required_fields if field not in data]

                if not missing_fields:
                    file_status = "有文件" if data.get('has_file') else "无文件"
                    exists_status = "存在" if data.get('file_exists') else "不存在"

                    self.log_test(
                        f"文件信息-文档{document_id}",
                        True,
                        f"标题: {data.get('title')} | 类型: {data.get('file_type')} | {file_status} | 物理文件{exists_status}"
                    )
                    return data
                else:
                    self.log_test(
                        f"文件信息-文档{document_id}",
                        False,
                        f"响应缺少字段: {missing_fields}",
                        data
                    )
                    return None

            elif response.status_code == 404:
                self.log_test(
                    f"文件信息-文档{document_id}",
                    False,
                    "文档不存在或未发布"
                )
                return None
            else:
                self.log_test(
                    f"文件信息-文档{document_id}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return None

        except Exception as e:
            self.log_test(f"文件信息-文档{document_id}", False, f"请求异常: {str(e)}")
            return None

    def test_file_download(self, document_id, preview=False):
        """测试文件下载接口"""
        mode = "预览" if preview else "下载"
        params = {"preview": "true"} if preview else {}

        try:
            response = requests.get(
                f"{self.api_base}/documents/{document_id}/download",
                params=params,
                stream=True  # 流式下载
            )

            if response.status_code == 200:
                # 检查响应头
                content_type = response.headers.get('Content-Type', '')
                content_disposition = response.headers.get('Content-Disposition', '')
                content_length = response.headers.get('Content-Length', '0')

                # 验证文件内容（读取前1KB）
                content_sample = b''
                for chunk in response.iter_content(chunk_size=1024):
                    content_sample = chunk
                    break

                file_size_kb = round(int(content_length) / 1024, 2) if content_length.isdigit() else "未知"

                self.log_test(
                    f"文件{mode}-文档{document_id}",
                    True,
                    f"成功 | 类型: {content_type} | 大小: {file_size_kb}KB | 头部: {content_disposition[:50]}..."
                )
                return True

            elif response.status_code == 404:
                error_data = response.json() if response.headers.get('Content-Type', '').startswith(
                    'application/json') else response.text
                self.log_test(
                    f"文件{mode}-文档{document_id}",
                    False,
                    f"文件不存在: {error_data}"
                )
                return False
            else:
                self.log_test(
                    f"文件{mode}-文档{document_id}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False

        except Exception as e:
            self.log_test(f"文件{mode}-文档{document_id}", False, f"请求异常: {str(e)}")
            return False

    def test_file_stream(self, document_id):
        """测试文件流式传输接口"""
        try:
            response = requests.get(
                f"{self.api_base}/documents/{document_id}/stream",
                stream=True
            )

            if response.status_code == 200:
                # 检查响应头
                content_type = response.headers.get('Content-Type', '')
                content_length = response.headers.get('Content-Length', '0')
                accept_ranges = response.headers.get('Accept-Ranges', '')

                # 验证流式传输（读取前几个chunk）
                chunk_count = 0
                total_bytes = 0

                for chunk in response.iter_content(chunk_size=8192):
                    chunk_count += 1
                    total_bytes += len(chunk)
                    if chunk_count >= 3:  # 只读取前3个chunk测试
                        break

                file_size_kb = round(int(content_length) / 1024, 2) if content_length.isdigit() else "未知"

                self.log_test(
                    f"文件流传输-文档{document_id}",
                    True,
                    f"成功 | 类型: {content_type} | 大小: {file_size_kb}KB | 支持断点续传: {bool(accept_ranges)} | 已读取: {chunk_count}个块"
                )
                return True

            elif response.status_code == 404:
                error_data = response.json() if response.headers.get('Content-Type', '').startswith(
                    'application/json') else response.text
                self.log_test(
                    f"文件流传输-文档{document_id}",
                    False,
                    f"文件不存在: {error_data}"
                )
                return False
            else:
                self.log_test(
                    f"文件流传输-文档{document_id}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False

        except Exception as e:
            self.log_test(f"文件流传输-文档{document_id}", False, f"请求异常: {str(e)}")
            return False

    def test_invalid_document(self):
        """测试访问不存在的文档"""
        invalid_id = 99999

        # 测试文件信息
        response = requests.get(f"{self.api_base}/documents/{invalid_id}/info")
        if response.status_code == 404:
            self.log_test("无效文档-文件信息", True, "正确返回404错误")
        else:
            self.log_test("无效文档-文件信息", False, f"应该返回404，实际返回{response.status_code}")

        # 测试文件下载
        response = requests.get(f"{self.api_base}/documents/{invalid_id}/download")
        if response.status_code == 404:
            self.log_test("无效文档-文件下载", True, "正确返回404错误")
        else:
            self.log_test("无效文档-文件下载", False, f"应该返回404，实际返回{response.status_code}")

        # 测试文件流传输
        response = requests.get(f"{self.api_base}/documents/{invalid_id}/stream")
        if response.status_code == 404:
            self.log_test("无效文档-文件流传输", True, "正确返回404错误")
        else:
            self.log_test("无效文档-文件流传输", False, f"应该返回404，实际返回{response.status_code}")

    def save_test_results(self):
        """保存测试结果到文件"""
        results_file = "tech_square_file_test_results.json"

        summary = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r["success"]]),
            "failed_tests": len([r for r in self.test_results if not r["success"]]),
            "results": self.test_results
        }

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"📄 测试结果已保存到: {results_file}")
        return summary

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始技术广场文件访问功能测试")
        print("=" * 60)

        # 1. 模块健康检查
        if not self.test_module_health():
            print("❌ 模块健康检查失败，停止测试")
            return

        # 2. 获取已发布文档
        documents = self.get_published_documents()
        if not documents:
            print("❌ 没有已发布文档，无法进行文件访问测试")
            print("💡 请先通过文档管理模块发布一些包含文件的文档")
            return

        # 3. 测试前3个文档的文件访问功能
        test_documents = documents[:3]

        for doc in test_documents:
            doc_id = doc['id']
            doc_title = doc['title']
            file_type = doc.get('file_type', 'unknown')

            print(f"📄 测试文档: {doc_title} (ID: {doc_id}, 类型: {file_type})")
            print("-" * 40)

            # 获取文件信息
            file_info = self.test_file_info(doc_id)

            if file_info and file_info.get('has_file') and file_info.get('file_exists'):
                # 文件存在，测试下载和流传输
                self.test_file_download(doc_id, preview=False)  # 下载模式
                self.test_file_download(doc_id, preview=True)  # 预览模式
                self.test_file_stream(doc_id)  # 流式传输
            else:
                print(f"   ⚠️  文档 {doc_id} 没有可用的文件，跳过下载测试")

            print()

        # 4. 测试错误处理
        print("🔍 测试错误处理")
        print("-" * 40)
        self.test_invalid_document()

        # 5. 生成测试报告
        print("\n" + "=" * 60)
        print("📊 测试总结")
        summary = self.save_test_results()

        print(f"总测试数: {summary['total_tests']}")
        print(f"通过: {summary['passed_tests']} ✅")
        print(f"失败: {summary['failed_tests']} ❌")

        if summary['failed_tests'] > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")

        success_rate = (summary['passed_tests'] / summary['total_tests']) * 100
        print(f"\n成功率: {success_rate:.1f}%")

        if success_rate >= 80:
            print("🎉 测试基本通过！")
        else:
            print("⚠️  测试存在较多问题，请检查实现")


def main():
    """主函数"""
    print("技术广场文件访问功能测试脚本")
    print("测试服务器: http://localhost:8100")
    print()

    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:8100", timeout=5)
        print("✅ 服务器连接正常")
    except:
        print("❌ 无法连接到服务器，请确保FastAPI服务正在运行")
        print("启动命令: python -m uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload")
        return

    print()

    # 运行测试
    tester = TechSquareFileTest()
    tester.run_all_tests()


if __name__ == "__main__":
    main()