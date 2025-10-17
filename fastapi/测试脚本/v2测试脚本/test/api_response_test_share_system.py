import requests
import json
from datetime import datetime


class ShareSystemAPIResponseTest:
    def __init__(self):
        self.base_url = "http://localhost:8100/api"
        self.token = None

        # 为每种分享类型创建独立的文档
        self.test_documents = {
            "public": None,
            "private": None,
            "password": None
        }

        self.test_shares = {
            "public": {"id": None, "code": None},
            "private": {"id": None, "code": None},
            "password": {"id": None, "code": None}
        }

    def login(self):
        """登录获取token"""
        login_data = {
            "username_or_email": "abc",
            "password": "ljl18420"
        }

        response = requests.post(f"{self.base_url}/v1/user_auth/login", json=login_data)
        print(f"🔐 登录响应状态码: {response.status_code}")
        print(f"🔐 登录响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录失败")
            return False

    def get_headers(self):
        """获取认证头"""
        return {"Authorization": f"Bearer {self.token}"}

    def create_test_document(self, doc_type):
        """为指定类型创建测试文档"""
        doc_data = {
            "title": f"{doc_type}分享测试文档_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": f"# 这是一个用于测试{doc_type}分享功能的文档\n\n这个文档将被用来测试{doc_type}分享系统的各种功能。",
            "file_type": "md"
        }

        response = requests.post(
            f"{self.base_url}/v2/document_manager/documents",
            json=doc_data,
            headers=self.get_headers()
        )

        print(f"📄 创建{doc_type}文档响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            self.test_documents[doc_type] = result["id"]
            print(f"✅ 创建{doc_type}测试文档成功，ID: {result['id']}")
            return True
        else:
            print(f"❌ 创建{doc_type}测试文档失败")
            return False

    def test_module_connectivity(self):
        """测试模块连通性"""
        response = requests.get(f"{self.base_url}/v2/share_system/test")
        print(f"🔗 模块连通性测试状态码: {response.status_code}")
        print(f"🔗 模块连通性测试响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def test_create_public_share(self):
        """测试创建公开分享"""
        if not self.create_test_document("public"):
            return False

        share_data = {
            "document_id": self.test_documents["public"],
            "share_type": "public",
            "allow_download": True,
            "allow_comment": True,
            "expire_hours": 168
        }

        response = requests.post(
            f"{self.base_url}/v2/share_system/create",
            json=share_data,
            headers=self.get_headers()
        )

        print(f"🔗 创建公开分享响应状态码: {response.status_code}")
        print(f"🔗 创建公开分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            result = response.json()
            self.test_shares["public"]["id"] = result["id"]
            self.test_shares["public"]["code"] = result["share_code"]
            print(f"✅ 创建公开分享成功，ID: {result['id']}, Code: {result['share_code']}")
            return True
        else:
            print("❌ 创建公开分享失败")
            return False

    def test_create_private_share(self):
        """测试创建私有分享"""
        if not self.create_test_document("private"):
            return False

        share_data = {
            "document_id": self.test_documents["private"],
            "share_type": "private",
            "allow_download": True,
            "allow_comment": True,
            "expire_hours": 168
        }

        response = requests.post(
            f"{self.base_url}/v2/share_system/create",
            json=share_data,
            headers=self.get_headers()
        )

        print(f"🔒 创建私有分享响应状态码: {response.status_code}")
        print(f"🔒 创建私有分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            result = response.json()
            self.test_shares["private"]["id"] = result["id"]
            self.test_shares["private"]["code"] = result["share_code"]
            print(f"✅ 创建私有分享成功，ID: {result['id']}, Code: {result['share_code']}")
            return True
        else:
            print("❌ 创建私有分享失败")
            return False

    def test_create_password_share(self):
        """测试创建密码保护分享"""
        if not self.create_test_document("password"):
            return False

        share_data = {
            "document_id": self.test_documents["password"],
            "share_type": "password",
            "share_password": "test123",
            "allow_download": True,
            "allow_comment": True,
            "expire_hours": 168
        }

        response = requests.post(
            f"{self.base_url}/v2/share_system/create",
            json=share_data,
            headers=self.get_headers()
        )

        print(f"🔑 创建密码分享响应状态码: {response.status_code}")
        print(f"🔑 创建密码分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            result = response.json()
            self.test_shares["password"]["id"] = result["id"]
            self.test_shares["password"]["code"] = result["share_code"]
            print(f"✅ 创建密码分享成功，ID: {result['id']}, Code: {result['share_code']}")
            return True
        else:
            print("❌ 创建密码分享失败")
            return False

    def test_access_public_share(self):
        """测试匿名访问公开分享"""
        if not self.test_shares["public"]["code"]:
            print("❌ 没有公开分享码，跳过测试")
            return False

        # 匿名访问（不带token）
        access_data = {}
        response = requests.post(
            f"{self.base_url}/v2/share_system/public/{self.test_shares['public']['code']}",
            json=access_data
        )

        print(f"👁️ 匿名访问公开分享响应状态码: {response.status_code}")
        print(f"👁️ 匿名访问公开分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def test_access_private_share_without_auth(self):
        """测试匿名访问私有分享（应该失败）"""
        if not self.test_shares["private"]["code"]:
            print("❌ 没有私有分享码，跳过测试")
            return False

        # 匿名访问（不带token）
        access_data = {}
        response = requests.post(
            f"{self.base_url}/v2/share_system/public/{self.test_shares['private']['code']}",
            json=access_data
        )

        print(f"🔒 匿名访问私有分享响应状态码: {response.status_code}")
        print(f"🔒 匿名访问私有分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        # 私有分享匿名访问应该返回401
        return response.status_code == 401

    def test_access_private_share_with_auth(self):
        """测试登录后访问私有分享（应该成功）"""
        if not self.test_shares["private"]["code"]:
            print("❌ 没有私有分享码，跳过测试")
            return False

        # 带token访问
        access_data = {}
        response = requests.post(
            f"{self.base_url}/v2/share_system/public/{self.test_shares['private']['code']}",
            json=access_data,
            headers=self.get_headers()
        )

        print(f"🔓 登录访问私有分享响应状态码: {response.status_code}")
        print(f"🔓 登录访问私有分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def test_access_password_share_without_password(self):
        """测试访问密码分享但不提供密码（应该失败）"""
        if not self.test_shares["password"]["code"]:
            print("❌ 没有密码分享码，跳过测试")
            return False

        # 不提供密码访问
        access_data = {}
        response = requests.post(
            f"{self.base_url}/v2/share_system/public/{self.test_shares['password']['code']}",
            json=access_data
        )

        print(f"🔑❌ 无密码访问密码分享响应状态码: {response.status_code}")
        print(f"🔑❌ 无密码访问密码分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400

    def test_access_password_share_with_wrong_password(self):
        """测试访问密码分享但提供错误密码（应该失败）"""
        if not self.test_shares["password"]["code"]:
            print("❌ 没有密码分享码，跳过测试")
            return False

        # 提供错误密码
        access_data = {"password": "wrong123"}
        response = requests.post(
            f"{self.base_url}/v2/share_system/public/{self.test_shares['password']['code']}",
            json=access_data
        )

        print(f"🔑❌ 错误密码访问密码分享响应状态码: {response.status_code}")
        print(f"🔑❌ 错误密码访问密码分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 400

    def test_access_password_share_with_correct_password(self):
        """测试访问密码分享并提供正确密码（应该成功）"""
        if not self.test_shares["password"]["code"]:
            print("❌ 没有密码分享码，跳过测试")
            return False

        # 提供正确密码
        access_data = {"password": "test123"}
        response = requests.post(
            f"{self.base_url}/v2/share_system/public/{self.test_shares['password']['code']}",
            json=access_data
        )

        print(f"🔑✅ 正确密码访问密码分享响应状态码: {response.status_code}")
        print(f"🔑✅ 正确密码访问密码分享响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def test_get_my_shares(self):
        """测试获取我的分享列表"""
        response = requests.get(
            f"{self.base_url}/v2/share_system/my-shares?page=1&size=10",
            headers=self.get_headers()
        )

        print(f"📋 获取分享列表响应状态码: {response.status_code}")
        print(f"📋 获取分享列表响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def test_get_share_stats(self):
        """测试获取分享统计"""
        response = requests.get(
            f"{self.base_url}/v2/share_system/stats",
            headers=self.get_headers()
        )

        print(f"📈 获取分享统计响应状态码: {response.status_code}")
        print(f"📈 获取分享统计响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def test_get_config(self):
        """测试获取配置"""
        response = requests.get(f"{self.base_url}/v2/share_system/config")

        print(f"⚙️ 获取配置响应状态码: {response.status_code}")
        print(f"⚙️ 获取配置响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200

    def run_all_tests(self):
        """运行所有API响应格式测试"""
        print("🚀 开始Share System模块完整API响应格式测试")
        print("=" * 70)

        # 登录
        if not self.login():
            return

        # 测试各个接口
        tests = [
            ("模块连通性", self.test_module_connectivity),
            ("创建公开分享", self.test_create_public_share),
            ("创建私有分享", self.test_create_private_share),
            ("创建密码分享", self.test_create_password_share),
            ("匿名访问公开分享", self.test_access_public_share),
            ("匿名访问私有分享(应失败)", self.test_access_private_share_without_auth),
            ("登录访问私有分享", self.test_access_private_share_with_auth),
            ("无密码访问密码分享(应失败)", self.test_access_password_share_without_password),
            ("错误密码访问密码分享(应失败)", self.test_access_password_share_with_wrong_password),
            ("正确密码访问密码分享", self.test_access_password_share_with_correct_password),
            ("获取分享列表", self.test_get_my_shares),
            ("获取分享统计", self.test_get_share_stats),
            ("获取配置", self.test_get_config),
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 测试: {test_name}")
            print("-" * 50)
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"{'✅' if result else '❌'} {test_name}: {'通过' if result else '失败'}")
            except Exception as e:
                print(f"❌ {test_name}: 异常 - {str(e)}")
                results.append((test_name, False))

        # 总结
        print("\n" + "=" * 70)
        print("📊 完整API响应格式测试总结:")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            print(f"{'✅' if result else '❌'} {test_name}")

        print(f"\n🎯 通过率: {passed}/{total} ({passed / total * 100:.1f}%)")

        if passed == total:
            print("🎉 所有API响应格式测试通过！三种分享类型都正常工作。")
        else:
            print("⚠️ 部分测试失败，请检查API实现。")


if __name__ == "__main__":
    tester = ShareSystemAPIResponseTest()
    tester.run_all_tests()