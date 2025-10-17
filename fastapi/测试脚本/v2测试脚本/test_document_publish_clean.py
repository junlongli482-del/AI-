import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8100"
API_PREFIX = "/api/v2/document_publish"

# 测试用户凭据（使用现有用户）
TEST_USER = {
    "username_or_email": "abc",
    "password": "ljl18420"
}


class DocumentPublishTester:
    def __init__(self):
        self.base_url = BASE_URL + API_PREFIX
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_document_id = None

    def login(self):
        """登录获取token"""
        print("\n=== 1. 用户登录 ===")

        login_url = f"{BASE_URL}/api/v1/user_auth/login"
        response = requests.post(login_url, json=TEST_USER)

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def test_module_connection(self):
        """测试模块连通性"""
        print("\n=== 2. 测试模块连通性 ===")

        response = requests.get(f"{self.base_url}/test")

        if response.status_code == 200:
            data = response.json()
            print("✅ 模块连通性正常")
            print(f"📋 功能列表: {', '.join(data['features'])}")
            return True
        else:
            print(f"❌ 模块连通性异常: {response.text}")
            return False

    def get_publish_config(self):
        """获取发布配置"""
        print("\n=== 3. 获取发布配置 ===")

        response = requests.get(f"{self.base_url}/config")

        if response.status_code == 200:
            data = response.json()["data"]
            print("✅ 获取配置成功")
            print(f"📊 发布状态: {list(data['publish_statuses'].keys())}")
            print(f"🔄 操作类型: {list(data['action_types'].keys())}")
            return True
        else:
            print(f"❌ 获取配置失败: {response.text}")
            return False

    def create_test_document(self):
        """创建测试文档"""
        print("\n=== 4. 创建测试文档 ===")

        # 使用文档管理模块创建文档
        doc_url = f"{BASE_URL}/api/v2/document_manager/documents"
        doc_data = {
            "title": f"发布测试文档 {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": "# 测试文档\n\n这是一个用于测试发布功能的文档。\n\n## 内容说明\n\n- 测试AI审核\n- 测试发布流程\n- 测试状态管理",
            "file_type": "md",
            "summary": "用于测试发布功能的示例文档"
        }

        response = requests.post(doc_url, json=doc_data, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            self.test_document_id = data["id"]
            print(f"✅ 创建测试文档成功 (ID: {self.test_document_id})")
            return True
        else:
            print(f"❌ 创建测试文档失败: {response.text}")
            return False

    def submit_publish(self):
        """提交发布申请"""
        print("\n=== 5. 提交发布申请 ===")

        if not self.test_document_id:
            print("❌ 无测试文档ID")
            return False

        publish_data = {
            "document_id": self.test_document_id,
            "publish_reason": "测试发布流程，验证AI审核功能",
            "publish_config": {
                "auto_featured": False,
                "allow_comments": True
            }
        }

        response = requests.post(
            f"{self.base_url}/submit",
            json=publish_data,
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 提交发布成功")
            print(f"📄 发布状态: {data['publish_status']}")
            print(f"🔍 审核ID: {data.get('review_id', '未设置')}")
            return True
        else:
            print(f"❌ 提交发布失败: {response.text}")
            return False

    def check_publish_status(self):
        """检查发布状态"""
        print("\n=== 6. 检查发布状态 ===")

        if not self.test_document_id:
            print("❌ 无测试文档ID")
            return False

        response = requests.get(
            f"{self.base_url}/status/{self.test_document_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()["data"]
            print(f"✅ 获取状态成功")
            print(f"📊 发布状态: {data['publish_status']}")
            print(f"👀 浏览量: {data['view_count']}")
            print(f"⭐ 是否精选: {data['is_featured']}")
            return True
        else:
            print(f"❌ 获取状态失败: {response.text}")
            return False

    def get_publish_detail(self):
        """获取发布详情"""
        print("\n=== 7. 获取发布详情 ===")

        if not self.test_document_id:
            print("❌ 无测试文档ID")
            return False

        response = requests.get(
            f"{self.base_url}/document/{self.test_document_id}",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取详情成功")
            print(f"📄 文档标题: {data['title']}")
            print(f"📅 创建时间: {data['created_at']}")
            print(f"📋 发布记录: {'存在' if data['publish_record'] else '不存在'}")
            print(f"📚 历史记录数: {len(data['publish_history'])}")
            return True
        else:
            print(f"❌ 获取详情失败: {response.text}")
            return False

    def get_my_records(self):
        """获取我的发布记录"""
        print("\n=== 8. 获取我的发布记录 ===")

        response = requests.get(
            f"{self.base_url}/my-records?page=1&size=10",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()["data"]
            print(f"✅ 获取记录成功")
            print(f"📊 总数: {data['total']}")
            print(f"📄 当前页: {data['page']}/{data['pages']}")
            print(f"📋 记录数: {len(data['items'])}")
            return True
        else:
            print(f"❌ 获取记录失败: {response.text}")
            return False

    def get_publish_stats(self):
        """获取发布统计"""
        print("\n=== 9. 获取发布统计 ===")

        # 个人统计
        response = requests.get(
            f"{self.base_url}/stats",
            headers=self.headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 个人统计获取成功")
            print(f"📊 已发布: {data['total_published']}")
            print(f"📝 草稿: {data['total_drafts']}")
            print(f"🔍 待审核: {data['pending_review']}")
            print(f"📅 今日发布: {data['today_published']}")
            print(f"⭐ 精选数: {data['featured_count']}")
            print(f"👀 总浏览: {data['total_views']}")
            return True
        else:
            print(f"❌ 获取统计失败: {response.text}")
            return False

    def get_published_documents(self):
        """获取已发布文档列表"""
        print("\n=== 10. 获取已发布文档 ===")

        response = requests.get(f"{self.base_url}/published?page=1&size=10")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取列表成功")
            print(f"📊 总数: {data['total']}")
            print(f"📄 当前页: {data['page']}/{data['pages']}")
            print(f"📋 文档数: {len(data['items'])}")
            return True
        else:
            print(f"❌ 获取列表失败: {response.text}")
            return False

    def test_view_increment(self):
        """测试浏览量增加"""
        print("\n=== 11. 测试浏览量增加 ===")

        if not self.test_document_id:
            print("❌ 无测试文档ID")
            return False

        # 增加浏览量（不需要认证）
        response = requests.post(f"{self.base_url}/view/{self.test_document_id}")

        if response.status_code == 200:
            print("✅ 浏览量增加成功")
            return True
        else:
            print(f"❌ 浏览量增加失败: {response.text}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Document Publish模块测试")
        print("=" * 50)

        test_methods = [
            self.login,
            self.test_module_connection,
            self.get_publish_config,
            self.create_test_document,
            self.submit_publish,
            self.check_publish_status,
            self.get_publish_detail,
            self.get_my_records,
            self.get_publish_stats,
            self.get_published_documents,
            self.test_view_increment,
        ]

        passed = 0
        total = len(test_methods)

        for test_method in test_methods:
            try:
                if test_method():
                    passed += 1
                else:
                    print(f"⚠️ 测试失败: {test_method.__name__}")
            except Exception as e:
                print(f"💥 测试异常: {test_method.__name__} - {str(e)}")

        print("\n" + "=" * 50)
        print(f"📊 测试完成: {passed}/{total} 通过")

        if passed == total:
            print("🎉 所有测试通过! Document Publish模块运行正常")
        else:
            print("⚠️ 部分测试失败，请检查相关功能")


if __name__ == "__main__":
    tester = DocumentPublishTester()
    tester.run_all_tests()