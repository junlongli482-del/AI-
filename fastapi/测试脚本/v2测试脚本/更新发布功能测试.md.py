"""
文档更新功能测试脚本
测试 PUT /api/v2/document_publish/update/{document_id} 接口
"""
import requests
import json
import time


class DocumentUpdateTester:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.token = None
        self.test_document_id = None

    def login(self):
        """登录获取token"""
        login_url = f"{self.base_url}/api/v1/user_auth/login"
        login_data = {
            "username_or_email": "abc",
            "password": "ljl18420"
        }

        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def find_published_document(self):
        """查找一个已发布的文档用于测试"""
        url = f"{self.base_url}/api/v2/document_publish/my-records"

        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            result = response.json()
            items = result.get("data", {}).get("items", [])

            for item in items:
                publish_record = item["publish_record"]
                if publish_record["publish_status"] == "published":
                    self.test_document_id = publish_record["document_id"]
                    print(f"✅ 找到已发布文档 ID: {self.test_document_id}")
                    return True

            print("⚠️ 没有找到已发布的文档")
            return False
        else:
            print(f"❌ 获取发布记录失败: {response.text}")
            return False

    def test_update_document(self):
        """测试更新文档"""
        if not self.test_document_id:
            print("❌ 没有可测试的文档ID")
            return False

        print(f"\n📝 测试更新文档 ID: {self.test_document_id}")

        url = f"{self.base_url}/api/v2/document_publish/update/{self.test_document_id}"

        update_data = {
            "title": f"更新测试文档 - {int(time.time())}",
            "content": f"# 更新后的内容\n\n这是在 {time.strftime('%Y-%m-%d %H:%M:%S')} 更新的内容。\n\n## 更新说明\n- 修改了标题\n- 更新了内容\n- 添加了时间戳",
            "summary": f"这是更新后的摘要，更新时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
            "update_reason": "测试文档更新功能，验证AI审核流程"
        }

        response = requests.put(url, json=update_data, headers=self.get_headers())

        if response.status_code == 200:
            result = response.json()
            print("✅ 文档更新提交成功")
            print(f"   - 消息: {result['message']}")
            print(f"   - 版本: {result['update_info']['version']}")
            print(f"   - 审核状态: {result['update_info']['review_status']}")
            return True
        else:
            print(f"❌ 文档更新失败: {response.text}")
            return False

    def test_duplicate_update(self):
        """测试重复更新保护"""
        if not self.test_document_id:
            return False

        print(f"\n🔒 测试重复更新保护...")

        url = f"{self.base_url}/api/v2/document_publish/update/{self.test_document_id}"

        update_data = {
            "title": "重复更新测试",
            "update_reason": "测试重复更新保护机制"
        }

        response = requests.put(url, json=update_data, headers=self.get_headers())

        if response.status_code == 400:
            print("✅ 重复更新保护正常工作")
            print(f"   - 错误信息: {response.json().get('detail')}")
            return True
        else:
            print(f"⚠️ 重复更新保护可能有问题: {response.text}")
            return False

    def test_invalid_document(self):
        """测试无效文档ID"""
        print(f"\n🚫 测试无效文档ID...")

        url = f"{self.base_url}/api/v2/document_publish/update/99999"

        update_data = {
            "title": "无效文档测试",
            "update_reason": "测试无效文档ID"
        }

        response = requests.put(url, json=update_data, headers=self.get_headers())

        if response.status_code == 404:
            print("✅ 无效文档ID检查正常")
            print(f"   - 错误信息: {response.json().get('detail')}")
            return True
        else:
            print(f"⚠️ 无效文档ID检查可能有问题: {response.text}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始文档更新功能测试")
        print("=" * 50)

        if not self.login():
            return

        if not self.find_published_document():
            print("⚠️ 需要先有已发布的文档才能测试更新功能")
            return

        tests = [
            ("文档更新功能", self.test_update_document),
            ("重复更新保护", self.test_duplicate_update),
            ("无效文档检查", self.test_invalid_document),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {str(e)}")

        print("\n" + "=" * 50)
        print(f"📊 测试完成: {passed}/{total} 通过")

        if self.test_document_id:
            print(f"\n💡 测试文档ID: {self.test_document_id}")
            print("可以在技术广场查看更新后的文档")


if __name__ == "__main__":
    tester = DocumentUpdateTester()
    tester.run_all_tests()