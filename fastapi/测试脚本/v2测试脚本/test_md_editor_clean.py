import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8100"
USERNAME = "abc"  # 使用现有用户
PASSWORD = "ljl18420"


class MDEditorTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.session_id = None
        self.optimization_id = None

    def login(self):
        """用户登录获取token"""
        print("🔐 正在登录...")

        login_data = {
            "username_or_email": USERNAME,
            "password": PASSWORD
        }

        response = requests.post(f"{self.base_url}/api/v1/user_auth/login", json=login_data)

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            print(f"✅ 登录成功! Token: {self.token[:20]}...")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def get_headers(self):
        """获取认证头"""
        return {"Authorization": f"Bearer {self.token}"}

    def test_module_basic(self):
        """测试模块基础功能"""
        print("\n📋 测试模块基础功能...")

        # 测试接口
        response = requests.get(f"{self.base_url}/api/v2/md_editor/test")
        if response.status_code == 200:
            print("✅ 模块测试接口正常")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 模块测试接口失败: {response.text}")
            return False

        # 获取配置
        response = requests.get(f"{self.base_url}/api/v2/md_editor/config", headers=self.get_headers())
        if response.status_code == 200:
            print("✅ 编辑器配置获取成功")
            config = response.json()
            print(f"   优化类型数量: {len(config['optimization_types'])}")
        else:
            print(f"❌ 获取配置失败: {response.text}")

        return True

    def test_create_session(self):
        """测试创建编辑器会话"""
        print("\n📝 测试创建编辑器会话...")

        session_data = {
            "title": "测试MD文档",
            "content": "# 测试标题\n\n这是一个测试文档的内容。\n\n## 子标题\n\n- 列表项1\n- 列表项2",
            "session_type": "new_document"
        }

        response = requests.post(
            f"{self.base_url}/api/v2/md_editor/sessions",
            json=session_data,
            headers=self.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            self.session_id = data["id"]
            print(f"✅ 会话创建成功! ID: {self.session_id}")
            print(f"   标题: {data['title']}")
            print(f"   类型: {data['session_type']}")
            return True
        else:
            print(f"❌ 创建会话失败: {response.text}")
            return False

    def test_update_session(self):
        """测试更新会话"""
        print("\n✏️ 测试更新会话...")

        update_data = {
            "content": "# 更新后的标题\n\n这是更新后的内容。\n\n## 新的子标题\n\n更多内容...",
            "title": "更新后的测试文档"
        }

        response = requests.put(
            f"{self.base_url}/api/v2/md_editor/sessions/{self.session_id}",
            json=update_data,
            headers=self.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ 会话更新成功!")
            print(f"   新标题: {data['title']}")
            return True
        else:
            print(f"❌ 更新会话失败: {response.text}")
            return False

    def test_ai_optimization(self):
        """测试AI优化功能"""
        print("\n🤖 测试AI优化功能...")

        optimize_data = {
            "content": "# 测试文档\n\n这个文档需要优化。内容比较简单，希望AI能够帮助改进。",
            "optimization_type": "general"
        }

        response = requests.post(
            f"{self.base_url}/api/v2/md_editor/sessions/{self.session_id}/optimize",
            json=optimize_data,
            headers=self.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            self.optimization_id = data["optimization_id"]
            print("✅ AI优化成功!")
            print(f"   优化ID: {self.optimization_id}")
            print(f"   成功状态: {data['success']}")
            print(f"   原始内容长度: {len(data['original_content'])}")
            print(f"   优化内容长度: {len(data['optimized_content'])}")
            print(f"   优化内容预览: {data['optimized_content'][:100]}...")
            return True
        else:
            print(f"❌ AI优化失败: {response.text}")
            return False

    def test_apply_optimization(self):
        """测试应用优化结果"""
        if not self.optimization_id:
            print("⚠️ 跳过应用优化测试（没有优化ID）")
            return True

        print("\n✨ 测试应用优化结果...")

        response = requests.post(
            f"{self.base_url}/api/v2/md_editor/sessions/{self.session_id}/apply-optimization/{self.optimization_id}",
            headers=self.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ 优化结果应用成功!")
            print(f"   消息: {data['message']}")
            return True
        else:
            print(f"❌ 应用优化失败: {response.text}")
            return False

    def test_get_sessions(self):
        """测试获取会话列表"""
        print("\n📋 测试获取会话列表...")

        response = requests.get(
            f"{self.base_url}/api/v2/md_editor/sessions?limit=10",
            headers=self.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取会话列表成功! 共 {len(data)} 个会话")
            if data:
                print(f"   最新会话: {data[0]['title']}")
            return True
        else:
            print(f"❌ 获取会话列表失败: {response.text}")
            return False

    def test_get_stats(self):
        """测试获取统计信息"""
        print("\n📊 测试获取统计信息...")

        response = requests.get(
            f"{self.base_url}/api/v2/md_editor/stats",
            headers=self.get_headers()
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ 获取统计信息成功!")
            print(f"   总会话数: {data['total_sessions']}")
            print(f"   草稿数: {data['draft_sessions']}")
            print(f"   总优化次数: {data['total_optimizations']}")
            return True
        else:
            print(f"❌ 获取统计信息失败: {response.text}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 MD Editor 模块完整测试")
        print("=" * 50)

        # 登录
        if not self.login():
            return False

        # 运行测试
        tests = [
            self.test_module_basic,
            self.test_create_session,
            self.test_update_session,
            self.test_ai_optimization,
            self.test_apply_optimization,
            self.test_get_sessions,
            self.test_get_stats
        ]

        success_count = 0
        for test in tests:
            try:
                if test():
                    success_count += 1
                time.sleep(1)  # 避免请求过快
            except Exception as e:
                print(f"❌ 测试异常: {e}")

        print("\n" + "=" * 50)
        print(f"🎯 测试完成! 成功: {success_count}/{len(tests)}")

        if success_count == len(tests):
            print("🎉 所有测试通过!")
            return True
        else:
            print("⚠️ 部分测试失败，请检查日志")
            return False


if __name__ == "__main__":
    tester = MDEditorTester()
    tester.run_all_tests()