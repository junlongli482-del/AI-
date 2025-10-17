import requests
import json
from datetime import datetime
import random
import string


class APIResponseTester:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.access_token = None

    def test_login_response(self):
        """测试登录接口的真实响应格式"""
        print("🔍 测试登录接口响应格式...")

        login_data = {
            "username_or_email": "abc",
            "password": "ljl18420"
        }

        try:
            response = requests.post(f"{self.base_url}/api/v1/user_auth/login", json=login_data)

            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                print(f"JSON格式: {json.dumps(result, indent=2, ensure_ascii=False)}")

                # 尝试提取token
                if "access_token" in result:
                    self.access_token = result["access_token"]
                    print(f"✅ Token提取成功: {self.access_token[:20]}...")
                elif "data" in result and "access_token" in result["data"]:
                    self.access_token = result["data"]["access_token"]
                    print(f"✅ Token提取成功(嵌套): {self.access_token[:20]}...")
                else:
                    print("❌ 无法找到access_token字段")
                    return False

                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 登录测试异常: {str(e)}")
            return False

    def test_create_document_response(self):
        """测试创建文档接口的真实响应格式"""
        if not self.access_token:
            print("❌ 没有有效的token，跳过文档创建测试")
            return False

        print("\n🔍 测试创建文档接口响应格式...")

        # 生成唯一标题
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
        title = f"API测试文档_{timestamp}_{random_suffix}"

        doc_data = {
            "title": title,
            "content": "这是用于测试API响应格式的文档内容",
            "file_type": "md",
            "summary": "API响应格式测试"
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v2/document_manager/documents",
                json=doc_data,
                headers=headers
            )

            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                print(f"JSON格式: {json.dumps(result, indent=2, ensure_ascii=False)}")

                # 分析ID字段位置
                document_id = None
                if "data" in result and "id" in result["data"]:
                    document_id = result["data"]["id"]
                    print(f"✅ 文档ID位置: result['data']['id'] = {document_id}")
                elif "id" in result:
                    document_id = result["id"]
                    print(f"✅ 文档ID位置: result['id'] = {document_id}")
                else:
                    print("❌ 无法找到文档ID字段")
                    print(f"可用字段: {list(result.keys())}")

                return document_id
            else:
                print(f"❌ 创建文档失败: {response.text}")
                return None

        except Exception as e:
            print(f"❌ 创建文档测试异常: {str(e)}")
            return None

    def test_other_apis(self, document_id):
        """测试其他相关接口的响应格式"""
        if not document_id:
            print("❌ 没有有效的文档ID，跳过其他API测试")
            return

        print(f"\n🔍 测试其他接口响应格式 (文档ID: {document_id})...")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # 测试点赞状态接口
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{document_id}/like-status",
                headers=headers
            )
            print(f"\n点赞状态接口:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
        except Exception as e:
            print(f"点赞状态接口异常: {str(e)}")

        # 测试收藏状态接口
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{document_id}/favorite-status",
                headers=headers
            )
            print(f"\n收藏状态接口:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
        except Exception as e:
            print(f"收藏状态接口异常: {str(e)}")

        # 测试文档统计接口
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{document_id}/stats"
            )
            print(f"\n文档统计接口:")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
        except Exception as e:
            print(f"文档统计接口异常: {str(e)}")

    def run_all_tests(self):
        """运行所有API响应格式测试"""
        print("🚀 开始API响应格式测试")
        print("=" * 60)

        # 1. 测试登录
        if not self.test_login_response():
            print("❌ 登录测试失败，停止后续测试")
            return

        # 2. 测试创建文档
        document_id = self.test_create_document_response()

        # 3. 测试其他接口
        self.test_other_apis(document_id)

        print("\n" + "=" * 60)
        print("📊 API响应格式测试完成")
        print("现在你可以根据上面的真实响应格式来修复测试脚本了！")


if __name__ == "__main__":
    tester = APIResponseTester()
    tester.run_all_tests()