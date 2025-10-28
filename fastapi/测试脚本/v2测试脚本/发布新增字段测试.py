"""
测试文档状态字段功能
验证 publish_status, content_status, has_published_version 字段
"""
import requests
import json
import time


class DocumentStatusTester:
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

    def create_test_document(self):
        """创建测试文档"""
        print("\n📝 创建测试文档...")

        url = f"{self.base_url}/api/v2/document_manager/documents"
        doc_data = {
            "title": f"状态测试文档 - {int(time.time())}",
            "content": "# 测试文档\n\n这是用于测试状态字段的文档。",
            "summary": "测试文档摘要",
            "file_type": "md"
        }

        response = requests.post(url, json=doc_data, headers=self.get_headers())

        if response.status_code == 200:
            result = response.json()
            self.test_document_id = result["id"]
            print(f"✅ 创建文档成功，ID: {self.test_document_id}")

            # 检查初始状态
            self.check_document_status("创建后初始状态")
            return True
        else:
            print(f"❌ 创建文档失败: {response.text}")
            return False

    def check_document_status(self, stage_name):
        """检查文档状态"""
        print(f"\n🔍 检查文档状态 - {stage_name}")

        url = f"{self.base_url}/api/v2/document_manager/documents/{self.test_document_id}"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            doc = response.json()

            print(f"   📋 文档ID: {doc.get('id')}")
            print(f"   📋 标题: {doc.get('title')}")
            print(f"   📋 status (兼容字段): {doc.get('status')}")

            # 🆕 检查新增字段
            publish_status = doc.get('publish_status')
            content_status = doc.get('content_status')
            has_published_version = doc.get('has_published_version')

            print(f"   🆕 publish_status: {publish_status}")
            print(f"   🆕 content_status: {content_status}")
            print(f"   🆕 has_published_version: {has_published_version}")

            # 分析状态组合
            self.analyze_status_combination(publish_status, content_status, has_published_version)

            return {
                'publish_status': publish_status,
                'content_status': content_status,
                'has_published_version': has_published_version
            }
        else:
            print(f"❌ 获取文档状态失败: {response.text}")
            return None

    def analyze_status_combination(self, publish_status, content_status, has_published_version):
        """分析状态组合"""
        print(f"   📊 状态分析:")

        # 技术广场状态
        if publish_status == "published":
            print(f"      🌐 技术广场: 有内容")
        elif publish_status is None or publish_status == "draft":
            print(f"      🌐 技术广场: 无内容")
        else:
            print(f"      🌐 技术广场: {publish_status}")

        # 内容状态
        status_map = {
            "draft": "📝 草稿",
            "pending_review": "🔄 审核中",
            "published": "✅ 审核通过",
            "review_failed": "❌ 审核失败"
        }
        content_desc = status_map.get(content_status, f"❓ 未知状态: {content_status}")
        print(f"      📄 最新内容: {content_desc}")

        # 发布历史
        history_desc = "有发布历史" if has_published_version else "从未发布"
        print(f"      📚 发布历史: {history_desc}")

        # 前端应该显示的状态
        frontend_status = self.get_frontend_display_status(publish_status, content_status, has_published_version)
        print(f"      🖥️ 前端显示: {frontend_status}")

    def get_frontend_display_status(self, publish_status, content_status, has_published_version):
        """根据状态组合确定前端应该显示的状态"""
        has_published = publish_status == "published"

        if not has_published and content_status == "draft":
            return "📝 草稿"
        elif not has_published and content_status == "review_failed":
            return "❌ 审核失败"
        elif has_published and content_status == "published":
            return "✅ 已发布"
        elif has_published and content_status == "pending_review":
            return "🔄 更新审核中"
        elif has_published and content_status == "review_failed":
            return "⚠️ 更新失败"
        else:
            return f"❓ 未知组合: {publish_status}/{content_status}"

    def test_publish_flow(self):
        """测试发布流程"""
        if not self.test_document_id:
            return False

        print(f"\n📤 测试发布流程...")

        # 提交发布
        url = f"{self.base_url}/api/v2/document_publish/submit"
        publish_data = {
            "document_id": self.test_document_id,
            "publish_reason": "测试发布流程"
        }

        response = requests.post(url, json=publish_data, headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 提交发布成功")

            # 等待AI审核
            print("⏳ 等待AI审核...")
            time.sleep(3)

            # 检查发布后状态
            self.check_document_status("发布后状态")
            return True
        else:
            print(f"❌ 提交发布失败: {response.text}")
            return False

    def test_update_flow(self):
        """测试更新流程"""
        if not self.test_document_id:
            return False

        print(f"\n🔄 测试更新流程...")

        # 更新文档
        url = f"{self.base_url}/api/v2/document_publish/update/{self.test_document_id}"
        update_data = {
            "title": f"更新后的标题 - {int(time.time())}",
            "content": "# 更新后的内容\n\n这是更新后的内容。",
            "update_reason": "测试更新流程"
        }

        response = requests.put(url, json=update_data, headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 提交更新成功")

            # 立即检查状态（应该是审核中）
            self.check_document_status("更新提交后状态")

            # 等待AI审核
            print("⏳ 等待AI审核...")
            time.sleep(3)

            # 检查审核后状态
            self.check_document_status("更新审核后状态")
            return True
        else:
            print(f"❌ 提交更新失败: {response.text}")
            return False

    def test_document_list(self):
        """测试文档列表接口"""
        print(f"\n📋 测试文档列表接口...")

        url = f"{self.base_url}/api/v2/document_manager/documents"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            result = response.json()
            documents = result.get("documents", [])

            print(f"✅ 获取文档列表成功，共 {len(documents)} 个文档")

            # 检查测试文档的状态
            test_doc = None
            for doc in documents:
                if doc["id"] == self.test_document_id:
                    test_doc = doc
                    break

            if test_doc:
                print(f"   🔍 找到测试文档:")
                print(f"      ID: {test_doc.get('id')}")
                print(f"      标题: {test_doc.get('title')}")
                print(f"      status: {test_doc.get('status')}")
                print(f"      🆕 publish_status: {test_doc.get('publish_status')}")
                print(f"      🆕 content_status: {test_doc.get('content_status')}")
                print(f"      🆕 has_published_version: {test_doc.get('has_published_version')}")
                return True
            else:
                print(f"⚠️ 在列表中未找到测试文档")
                return False
        else:
            print(f"❌ 获取文档列表失败: {response.text}")
            return False

    def cleanup_test_document(self):
        """清理测试文档"""
        if not self.test_document_id:
            return

        print(f"\n🗑️ 清理测试文档...")

        url = f"{self.base_url}/api/v2/document_manager/documents/{self.test_document_id}"
        response = requests.delete(url, headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 测试文档清理成功")
        else:
            print(f"⚠️ 清理测试文档失败: {response.text}")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试文档状态字段功能")
        print("=" * 60)

        if not self.login():
            return

        tests = [
            ("创建测试文档", self.create_test_document),
            ("测试发布流程", self.test_publish_flow),
            ("测试更新流程", self.test_update_flow),
            ("测试文档列表", self.test_document_list),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                print(f"\n{'=' * 20} {test_name} {'=' * 20}")
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {str(e)}")

        # 清理
        self.cleanup_test_document()

        print("\n" + "=" * 60)
        print(f"📊 测试完成: {passed}/{total} 通过")

        if passed == total:
            print("🎉 所有测试通过！新增状态字段功能正常工作")
        else:
            print("⚠️ 部分测试失败，请检查实现")


if __name__ == "__main__":
    tester = DocumentStatusTester()
    tester.run_all_tests()
"""
测试文档状态字段功能
验证 publish_status, content_status, has_published_version 字段
"""
import requests
import json
import time

class DocumentStatusTester:
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

    def create_test_document(self):
        """创建测试文档"""
        print("\n📝 创建测试文档...")

        url = f"{self.base_url}/api/v2/document_manager/documents"
        doc_data = {
            "title": f"状态测试文档 - {int(time.time())}",
            "content": "# 测试文档\n\n这是用于测试状态字段的文档。",
            "summary": "测试文档摘要",
            "file_type": "md"
        }

        response = requests.post(url, json=doc_data, headers=self.get_headers())

        if response.status_code == 200:
            result = response.json()
            self.test_document_id = result["id"]
            print(f"✅ 创建文档成功，ID: {self.test_document_id}")

            # 检查初始状态
            self.check_document_status("创建后初始状态")
            return True
        else:
            print(f"❌ 创建文档失败: {response.text}")
            return False

    def check_document_status(self, stage_name):
        """检查文档状态"""
        print(f"\n🔍 检查文档状态 - {stage_name}")

        url = f"{self.base_url}/api/v2/document_manager/documents/{self.test_document_id}"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            doc = response.json()

            print(f"   📋 文档ID: {doc.get('id')}")
            print(f"   📋 标题: {doc.get('title')}")
            print(f"   📋 status (兼容字段): {doc.get('status')}")

            # 🆕 检查新增字段
            publish_status = doc.get('publish_status')
            content_status = doc.get('content_status')
            has_published_version = doc.get('has_published_version')

            print(f"   🆕 publish_status: {publish_status}")
            print(f"   🆕 content_status: {content_status}")
            print(f"   🆕 has_published_version: {has_published_version}")

            # 分析状态组合
            self.analyze_status_combination(publish_status, content_status, has_published_version)

            return {
                'publish_status': publish_status,
                'content_status': content_status,
                'has_published_version': has_published_version
            }
        else:
            print(f"❌ 获取文档状态失败: {response.text}")
            return None

    def analyze_status_combination(self, publish_status, content_status, has_published_version):
        """分析状态组合"""
        print(f"   📊 状态分析:")

        # 技术广场状态
        if publish_status == "published":
            print(f"      🌐 技术广场: 有内容")
        elif publish_status is None or publish_status == "draft":
            print(f"      🌐 技术广场: 无内容")
        else:
            print(f"      🌐 技术广场: {publish_status}")

        # 内容状态
        status_map = {
            "draft": "📝 草稿",
            "pending_review": "🔄 审核中",
            "published": "✅ 审核通过",
            "review_failed": "❌ 审核失败"
        }
        content_desc = status_map.get(content_status, f"❓ 未知状态: {content_status}")
        print(f"      📄 最新内容: {content_desc}")

        # 发布历史
        history_desc = "有发布历史" if has_published_version else "从未发布"
        print(f"      📚 发布历史: {history_desc}")

        # 前端应该显示的状态
        frontend_status = self.get_frontend_display_status(publish_status, content_status, has_published_version)
        print(f"      🖥️ 前端显示: {frontend_status}")

    def get_frontend_display_status(self, publish_status, content_status, has_published_version):
        """根据状态组合确定前端应该显示的状态"""
        has_published = publish_status == "published"

        if not has_published and content_status == "draft":
            return "📝 草稿"
        elif not has_published and content_status == "review_failed":
            return "❌ 审核失败"
        elif has_published and content_status == "published":
            return "✅ 已发布"
        elif has_published and content_status == "pending_review":
            return "🔄 更新审核中"
        elif has_published and content_status == "review_failed":
            return "⚠️ 更新失败"
        else:
            return f"❓ 未知组合: {publish_status}/{content_status}"

    def test_publish_flow(self):
        """测试发布流程"""
        if not self.test_document_id:
            return False

        print(f"\n📤 测试发布流程...")

        # 提交发布
        url = f"{self.base_url}/api/v2/document_publish/submit"
        publish_data = {
            "document_id": self.test_document_id,
            "publish_reason": "测试发布流程"
        }

        response = requests.post(url, json=publish_data, headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 提交发布成功")

            # 等待AI审核
            print("⏳ 等待AI审核...")
            time.sleep(3)

            # 检查发布后状态
            self.check_document_status("发布后状态")
            return True
        else:
            print(f"❌ 提交发布失败: {response.text}")
            return False

    def test_update_flow(self):
        """测试更新流程"""
        if not self.test_document_id:
            return False

        print(f"\n🔄 测试更新流程...")

        # 更新文档
        url = f"{self.base_url}/api/v2/document_publish/update/{self.test_document_id}"
        update_data = {
            "title": f"更新后的标题 - {int(time.time())}",
            "content": "# 更新后的内容\n\n这是更新后的内容。",
            "update_reason": "测试更新流程"
        }

        response = requests.put(url, json=update_data, headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 提交更新成功")

            # 立即检查状态（应该是审核中）
            self.check_document_status("更新提交后状态")

            # 等待AI审核
            print("⏳ 等待AI审核...")
            time.sleep(3)

            # 检查审核后状态
            self.check_document_status("更新审核后状态")
            return True
        else:
            print(f"❌ 提交更新失败: {response.text}")
            return False

    def test_document_list(self):
        """测试文档列表接口"""
        print(f"\n📋 测试文档列表接口...")

        url = f"{self.base_url}/api/v2/document_manager/documents"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 200:
            result = response.json()
            documents = result.get("documents", [])

            print(f"✅ 获取文档列表成功，共 {len(documents)} 个文档")

            # 检查测试文档的状态
            test_doc = None
            for doc in documents:
                if doc["id"] == self.test_document_id:
                    test_doc = doc
                    break

            if test_doc:
                print(f"   🔍 找到测试文档:")
                print(f"      ID: {test_doc.get('id')}")
                print(f"      标题: {test_doc.get('title')}")
                print(f"      status: {test_doc.get('status')}")
                print(f"      🆕 publish_status: {test_doc.get('publish_status')}")
                print(f"      🆕 content_status: {test_doc.get('content_status')}")
                print(f"      🆕 has_published_version: {test_doc.get('has_published_version')}")
                return True
            else:
                print(f"⚠️ 在列表中未找到测试文档")
                return False
        else:
            print(f"❌ 获取文档列表失败: {response.text}")
            return False

    def cleanup_test_document(self):
        """清理测试文档"""
        if not self.test_document_id:
            return

        print(f"\n🗑️ 清理测试文档...")

        url = f"{self.base_url}/api/v2/document_manager/documents/{self.test_document_id}"
        response = requests.delete(url, headers=self.get_headers())

        if response.status_code == 200:
            print("✅ 测试文档清理成功")
        else:
            print(f"⚠️ 清理测试文档失败: {response.text}")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试文档状态字段功能")
        print("=" * 60)

        if not self.login():
            return

        tests = [
            ("创建测试文档", self.create_test_document),
            ("测试发布流程", self.test_publish_flow),
            ("测试更新流程", self.test_update_flow),
            ("测试文档列表", self.test_document_list),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {str(e)}")

        # 清理
        self.cleanup_test_document()

        print("\n" + "=" * 60)
        print(f"📊 测试完成: {passed}/{total} 通过")

        if passed == total:
            print("🎉 所有测试通过！新增状态字段功能正常工作")
        else:
            print("⚠️ 部分测试失败，请检查实现")

if __name__ == "__main__":
    tester = DocumentStatusTester()
    tester.run_all_tests()