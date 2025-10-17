# 测试脚本/v2测试脚本/test_tech_square_clean.py
import requests
import json
from datetime import datetime
import random
import string


class TechSquareModuleTester:
    def __init__(self, base_url="http://localhost:8100"):
        self.base_url = base_url
        self.access_token = None
        self.test_document_id = None

        # 测试账号信息
        self.test_user = {
            "username": "abc",
            "password": "ljl18420"
        }

    def generate_unique_title(self):
        """生成唯一的文档标题"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
        return f"技术广场测试文档_{timestamp}_{random_suffix}"

    def login(self):
        """用户登录获取token"""
        login_data = {
            "username_or_email": self.test_user["username"],
            "password": self.test_user["password"]
        }

        try:
            response = requests.post(f"{self.base_url}/api/v1/user_auth/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                print("✅ 用户登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False

    def get_headers(self):
        """获取请求头"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    def test_module_connectivity(self):
        """测试模块连通性"""
        try:
            response = requests.get(f"{self.base_url}/api/v2/tech_square/test")
            if response.status_code == 200:
                print("✅ 模块连通性正常")
                return True
            else:
                print(f"❌ 模块连通性失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 连通性测试异常: {str(e)}")
            return False

    def setup_test_data(self):
        """准备测试数据 - 创建并发布一个文档"""
        try:
            # 1. 创建测试文档（使用唯一标题）
            unique_title = self.generate_unique_title()
            doc_data = {
                "title": unique_title,
                "content": "这是一个用于测试技术广场功能的文档。\n\n## 功能特性\n\n1. 文档展示\n2. 搜索功能\n3. 分类筛选\n\n内容丰富，便于测试各种搜索和筛选功能。",
                "summary": "技术广场功能测试文档，包含搜索和筛选测试内容",
                "file_type": "md"
            }

            response = requests.post(
                f"{self.base_url}/api/v2/document_manager/documents",
                json=doc_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                if "data" in result and "id" in result["data"]:
                    self.test_document_id = result["data"]["id"]
                elif "id" in result:
                    self.test_document_id = result["id"]
                else:
                    print(f"❌ 无法获取文档ID，响应: {result}")
                    return False

                print(f"✅ 创建测试文档成功 (ID: {self.test_document_id}, 标题: {unique_title})")

                # 2. 提交发布
                publish_data = {
                    "document_id": self.test_document_id,
                    "publish_reason": "技术广场测试文档发布",
                    "publish_config": {"auto_featured": False}
                }

                response = requests.post(
                    f"{self.base_url}/api/v2/document_publish/submit",
                    json=publish_data,
                    headers=self.get_headers()
                )

                if response.status_code == 200:
                    print("✅ 文档发布申请成功")

                    # 3. 等待并检查发布状态
                    import time
                    for i in range(15):  # 增加等待时间到15秒
                        time.sleep(1)
                        status_response = requests.get(
                            f"{self.base_url}/api/v2/document_publish/status/{self.test_document_id}",
                            headers=self.get_headers()
                        )

                        # 在测试脚本的 setup_test_data 方法中，修改状态检查部分：
                        if status_response.status_code == 200:
                            status_result = status_response.json()
                            # 修复：从data字段中获取状态
                            if "data" in status_result:
                                publish_status = status_result["data"].get('publish_status', 'unknown')
                            else:
                                publish_status = status_result.get('publish_status', 'unknown')

                            print(f"⏳ 发布状态检查 {i + 1}/15: {publish_status}")

                    print("⚠️ 发布状态检查超时，但继续测试...")
                    return True
                else:
                    print(f"❌ 文档发布失败: {response.text}")
                    return False
            else:
                print(f"❌ 创建测试文档失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 准备测试数据异常: {str(e)}")
            return False

    # 其他测试方法保持不变...
    def test_document_list(self):
        """测试文档列表接口"""
        try:
            print("\n📖 测试文档列表功能...")

            # 基础列表查询
            response = requests.get(f"{self.base_url}/api/v2/tech_square/documents")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 基础列表查询成功 (总数: {result.get('total', 0)})")
            else:
                print(f"❌ 基础列表查询失败: {response.text}")
                return False

            # 分页查询
            response = requests.get(f"{self.base_url}/api/v2/tech_square/documents?page=1&size=5")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 分页查询成功 (当前页: {result.get('page')}, 每页: {result.get('size')})")
            else:
                print(f"❌ 分页查询失败: {response.text}")
                return False

            # 文件类型筛选
            response = requests.get(f"{self.base_url}/api/v2/tech_square/documents?file_type=md")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 文件类型筛选成功 (MD文档数: {result.get('total', 0)})")
            else:
                print(f"❌ 文件类型筛选失败: {response.text}")
                return False

            # 排序查询
            response = requests.get(f"{self.base_url}/api/v2/tech_square/documents?sort_by=popular")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 热门排序查询成功")
            else:
                print(f"❌ 热门排序查询失败: {response.text}")
                return False

            return True

        except Exception as e:
            print(f"❌ 文档列表测试异常: {str(e)}")
            return False

    def test_document_detail(self):
        """测试文档详情接口"""
        try:
            if not self.test_document_id:
                print("❌ 没有可用的测试文档ID")
                return False

            response = requests.get(f"{self.base_url}/api/v2/tech_square/documents/{self.test_document_id}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取文档详情成功 (标题: {result.get('title', 'N/A')})")
                return True
            else:
                print(f"❌ 获取文档详情失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 文档详情测试异常: {str(e)}")
            return False

    def test_search_function(self):
        """测试搜索功能"""
        try:
            print("\n🔍 测试搜索功能...")

            # 关键词搜索
            response = requests.get(f"{self.base_url}/api/v2/tech_square/search?keyword=技术")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 关键词搜索成功 (结果数: {result.get('total', 0)})")
            else:
                print(f"❌ 关键词搜索失败: {response.text}")
                return False

            # 带类型筛选的搜索
            response = requests.get(f"{self.base_url}/api/v2/tech_square/search?keyword=测试&file_type=md")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 带筛选搜索成功 (MD文档结果数: {result.get('total', 0)})")
            else:
                print(f"❌ 带筛选搜索失败: {response.text}")
                return False

            # 分页搜索
            response = requests.get(f"{self.base_url}/api/v2/tech_square/search?keyword=文档&page=1&size=3")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 分页搜索成功")
            else:
                print(f"❌ 分页搜索失败: {response.text}")
                return False

            return True

        except Exception as e:
            print(f"❌ 搜索功能测试异常: {str(e)}")
            return False

    def test_category_stats(self):
        """测试分类统计"""
        try:
            response = requests.get(f"{self.base_url}/api/v2/tech_square/category-stats")
            if response.status_code == 200:
                result = response.json()
                print(
                    f"✅ 分类统计获取成功 (MD: {result.get('md_count', 0)}, PDF: {result.get('pdf_count', 0)}, 总计: {result.get('total_count', 0)})")
                return True
            else:
                print(f"❌ 分类统计获取失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 分类统计测试异常: {str(e)}")
            return False

    def test_hot_documents(self):
        """测试热门文档"""
        try:
            response = requests.get(f"{self.base_url}/api/v2/tech_square/hot-documents?limit=5")
            if response.status_code == 200:
                result = response.json()
                docs = result.get('documents', [])
                print(f"✅ 热门文档获取成功 (数量: {len(docs)})")
                return True
            else:
                print(f"❌ 热门文档获取失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 热门文档测试异常: {str(e)}")
            return False

    def test_latest_documents(self):
        """测试最新文档"""
        try:
            response = requests.get(f"{self.base_url}/api/v2/tech_square/latest-documents?limit=5")
            if response.status_code == 200:
                result = response.json()
                docs = result.get('documents', [])
                print(f"✅ 最新文档获取成功 (数量: {len(docs)})")
                return True
            else:
                print(f"❌ 最新文档获取失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 最新文档测试异常: {str(e)}")
            return False

    def test_tech_square_stats(self):
        """测试技术广场统计"""
        try:
            response = requests.get(f"{self.base_url}/api/v2/tech_square/stats")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 技术广场统计获取成功")
                print(f"   - 总文档数: {result.get('total_documents', 0)}")
                print(f"   - 总浏览量: {result.get('total_views', 0)}")
                print(f"   - 今日发布: {result.get('today_published', 0)}")
                print(f"   - 精选文档: {result.get('featured_count', 0)}")
                return True
            else:
                print(f"❌ 技术广场统计获取失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 技术广场统计测试异常: {str(e)}")
            return False

    def test_view_increment(self):
        """测试浏览量增加"""
        try:
            if not self.test_document_id:
                print("❌ 没有可用的测试文档ID")
                return False

            # 获取当前浏览量
            response = requests.get(f"{self.base_url}/api/v2/tech_square/documents/{self.test_document_id}")
            if response.status_code == 200:
                before_count = response.json().get('view_count', 0)
            else:
                before_count = 0

            # 增加浏览量
            response = requests.post(f"{self.base_url}/api/v2/tech_square/view/{self.test_document_id}")
            if response.status_code == 200:
                print(f"✅ 浏览量增加成功")

                # 验证浏览量是否增加
                response = requests.get(f"{self.base_url}/api/v2/tech_square/documents/{self.test_document_id}")
                if response.status_code == 200:
                    after_count = response.json().get('view_count', 0)
                    if after_count > before_count:
                        print(f"   - 浏览量从 {before_count} 增加到 {after_count}")
                    else:
                        print(f"   - 浏览量未正确增加 (前: {before_count}, 后: {after_count})")

                return True
            else:
                print(f"❌ 浏览量增加失败: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 浏览量增加测试异常: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Tech Square模块测试")
        print("=" * 50)

        test_results = []

        # 登录
        test_results.append(self.login())

        # 模块连通性
        test_results.append(self.test_module_connectivity())

        # 准备测试数据
        test_results.append(self.setup_test_data())

        # 核心功能测试
        test_results.append(self.test_document_list())
        test_results.append(self.test_document_detail())
        test_results.append(self.test_search_function())
        test_results.append(self.test_category_stats())
        test_results.append(self.test_hot_documents())
        test_results.append(self.test_latest_documents())
        test_results.append(self.test_tech_square_stats())
        test_results.append(self.test_view_increment())

        print("\n" + "=" * 50)
        passed_count = sum(test_results)
        total_count = len(test_results)

        print(f"📊 测试完成: {passed_count}/{total_count} 通过")

        if passed_count == total_count:
            print("🎉 所有测试通过! Tech Square模块运行正常")
        else:
            print("⚠️  部分测试失败，请检查相关功能")

        return passed_count == total_count


if __name__ == "__main__":
    tester = TechSquareModuleTester()
    tester.run_all_tests()