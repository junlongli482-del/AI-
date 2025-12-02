"""
文档列表缓存功能测试脚本
功能：测试技术广场和个人文档列表的缓存效果
"""
import requests
import json
import time
from typing import Optional


class DocumentListCacheTest:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.access_token: Optional[str] = None

        print("🧪 [TEST] 文档列表缓存测试开始")
        print("🧪 [TEST] 基础URL:", self.base_url)
        print("=" * 80)

    def login(self) -> bool:
        """用户登录获取token"""
        print("\n🔐 [LOGIN] 开始用户登录...")

        login_url = f"{self.base_url}/api/v1/user_auth/login"
        login_data = {
            "username_or_email": "abc",
            "password": "ljl18420"
        }

        try:
            response = requests.post(login_url, json=login_data)

            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                print(f"✅ [LOGIN] 登录成功")
                print(f"🔑 [LOGIN] Token: {self.access_token[:20]}...")
                return True
            else:
                print(f"❌ [LOGIN] 登录失败: {response.status_code}")
                print(f"❌ [LOGIN] 错误信息: {response.text}")
                return False

        except Exception as e:
            print(f"❌ [LOGIN] 登录异常: {e}")
            return False

    def test_tech_square_list_cache(self):
        """测试技术广场文档列表缓存"""
        print("\n📄 [TEST_PUBLIC] 测试技术广场文档列表缓存")
        print("-" * 60)

        url = f"{self.base_url}/api/v2/tech_square/documents"
        params = {
            "page": 1,
            "size": 10
        }

        # 第一次请求（缓存未命中）
        print("🔍 [TEST_PUBLIC] 第一次请求（预期：缓存未命中）")
        start_time = time.time()

        try:
            response1 = requests.get(url, params=params)
            first_time = (time.time() - start_time) * 1000

            if response1.status_code == 200:
                result1 = response1.json()
                print(f"✅ [TEST_PUBLIC] 第一次请求成功，耗时: {first_time:.2f}ms")
                print(f"📊 [TEST_PUBLIC] 返回文档数: {len(result1.get('documents', []))}")
                print(f"📊 [TEST_PUBLIC] 总文档数: {result1.get('total', 0)}")

                cache_info = result1.get('cache_info', {})
                print(f"💾 [TEST_PUBLIC] 缓存状态: {'命中' if cache_info.get('cached') else '未命中'}")

                if '_route_debug_info' in result1:
                    debug_info = result1['_route_debug_info']
                    print(f"🔧 [TEST_PUBLIC] 路由耗时: {debug_info.get('route_total_time_ms', 0):.2f}ms")
            else:
                print(f"❌ [TEST_PUBLIC] 第一次请求失败: {response1.status_code}")
                print(f"❌ [TEST_PUBLIC] 错误信息: {response1.text}")
                return

        except Exception as e:
            print(f"❌ [TEST_PUBLIC] 第一次请求异常: {e}")
            return

        # 等待1秒
        time.sleep(1)

        # 第二次请求（缓存命中）
        print("\n🔍 [TEST_PUBLIC] 第二次请求（预期：缓存命中）")
        start_time = time.time()

        try:
            response2 = requests.get(url, params=params)
            second_time = (time.time() - start_time) * 1000

            if response2.status_code == 200:
                result2 = response2.json()
                print(f"✅ [TEST_PUBLIC] 第二次请求成功，耗时: {second_time:.2f}ms")

                cache_info = result2.get('cache_info', {})
                print(f"💾 [TEST_PUBLIC] 缓存状态: {'命中' if cache_info.get('cached') else '未命中'}")

                # 性能对比
                improvement = ((first_time - second_time) / first_time) * 100
                print(f"🚀 [TEST_PUBLIC] 性能提升: {improvement:.1f}%")
                print(f"⚡ [TEST_PUBLIC] 时间节省: {first_time - second_time:.2f}ms")

                # 数据一致性检查
                if result1.get('total') == result2.get('total'):
                    print(f"✅ [TEST_PUBLIC] 数据一致性检查通过")
                else:
                    print(f"❌ [TEST_PUBLIC] 数据一致性检查失败")

            else:
                print(f"❌ [TEST_PUBLIC] 第二次请求失败: {response2.status_code}")

        except Exception as e:
            print(f"❌ [TEST_PUBLIC] 第二次请求异常: {e}")

    def test_user_document_list_cache(self):
        """测试个人文档列表缓存"""
        if not self.access_token:
            print("\n❌ [TEST_USER] 跳过个人文档测试：未登录")
            return

        print("\n📄 [TEST_USER] 测试个人文档列表缓存")
        print("-" * 60)

        url = f"{self.base_url}/api/v2/document_manager/documents"
        params = {
            "page": 1,
            "page_size": 10
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        # 第一次请求（缓存未命中）
        print("🔍 [TEST_USER] 第一次请求（预期：缓存未命中）")
        start_time = time.time()

        try:
            response1 = requests.get(url, params=params, headers=headers)
            first_time = (time.time() - start_time) * 1000

            if response1.status_code == 200:
                result1 = response1.json()
                print(f"✅ [TEST_USER] 第一次请求成功，耗时: {first_time:.2f}ms")
                print(f"📊 [TEST_USER] 返回文档数: {len(result1.get('documents', []))}")
                print(f"📊 [TEST_USER] 总文档数: {result1.get('total', 0)}")

                cache_info = result1.get('cache_info', {})
                print(f"💾 [TEST_USER] 缓存状态: {'命中' if cache_info.get('cached') else '未命中'}")

            else:
                print(f"❌ [TEST_USER] 第一次请求失败: {response1.status_code}")
                print(f"❌ [TEST_USER] 错误信息: {response1.text}")
                return

        except Exception as e:
            print(f"❌ [TEST_USER] 第一次请求异常: {e}")
            return

        # 等待1秒
        time.sleep(1)

        # 第二次请求（缓存命中）
        print("\n🔍 [TEST_USER] 第二次请求（预期：缓存命中）")
        start_time = time.time()

        try:
            response2 = requests.get(url, params=params, headers=headers)
            second_time = (time.time() - start_time) * 1000

            if response2.status_code == 200:
                result2 = response2.json()
                print(f"✅ [TEST_USER] 第二次请求成功，耗时: {second_time:.2f}ms")

                cache_info = result2.get('cache_info', {})
                print(f"💾 [TEST_USER] 缓存状态: {'命中' if cache_info.get('cached') else '未命中'}")

                # 性能对比
                improvement = ((first_time - second_time) / first_time) * 100
                print(f"🚀 [TEST_USER] 性能提升: {improvement:.1f}%")
                print(f"⚡ [TEST_USER] 时间节省: {first_time - second_time:.2f}ms")

                # 数据一致性检查
                if result1.get('total') == result2.get('total'):
                    print(f"✅ [TEST_USER] 数据一致性检查通过")
                else:
                    print(f"❌ [TEST_USER] 数据一致性检查失败")

            else:
                print(f"❌ [TEST_USER] 第二次请求失败: {response2.status_code}")

        except Exception as e:
            print(f"❌ [TEST_USER] 第二次请求异常: {e}")

    def test_cache_isolation(self):
        """测试缓存隔离（不同参数生成不同缓存）"""
        print("\n🔒 [TEST_ISOLATION] 测试缓存隔离")
        print("-" * 60)

        base_url = f"{self.base_url}/api/v2/tech_square/documents"

        # 测试不同页码
        print("🔍 [TEST_ISOLATION] 测试不同页码的缓存隔离")

        params_page1 = {"page": 1, "size": 5}
        params_page2 = {"page": 2, "size": 5}

        try:
            # 请求第1页
            response1 = requests.get(base_url, params=params_page1)
            # 请求第2页
            response2 = requests.get(base_url, params=params_page2)

            if response1.status_code == 200 and response2.status_code == 200:
                result1 = response1.json()
                result2 = response2.json()

                cache1 = result1.get('cache_info', {})
                cache2 = result2.get('cache_info', {})

                print(f"📄 [TEST_ISOLATION] 第1页缓存状态: {'命中' if cache1.get('cached') else '未命中'}")
                print(f"📄 [TEST_ISOLATION] 第2页缓存状态: {'命中' if cache2.get('cached') else '未命中'}")

                if cache1.get('cache_key') != cache2.get('cache_key'):
                    print(f"✅ [TEST_ISOLATION] 缓存Key隔离正确")
                else:
                    print(f"❌ [TEST_ISOLATION] 缓存Key隔离失败")

        except Exception as e:
            print(f"❌ [TEST_ISOLATION] 缓存隔离测试异常: {e}")

        # 测试搜索参数
        print("\n🔍 [TEST_ISOLATION] 测试搜索参数的缓存隔离")

        params_no_search = {"page": 1, "size": 5}
        params_with_search = {"page": 1, "size": 5, "search": "test"}

        try:
            # 无搜索请求
            response1 = requests.get(base_url, params=params_no_search)
            # 有搜索请求
            response2 = requests.get(base_url, params=params_with_search)

            if response1.status_code == 200 and response2.status_code == 200:
                result1 = response1.json()
                result2 = response2.json()

                cache1 = result1.get('cache_info', {})
                cache2 = result2.get('cache_info', {})

                print(f"📄 [TEST_ISOLATION] 无搜索缓存状态: {'命中' if cache1.get('cached') else '未命中'}")
                print(f"📄 [TEST_ISOLATION] 有搜索缓存状态: {'命中' if cache2.get('cached') else '未命中'}")

                if cache1.get('cache_key') != cache2.get('cache_key'):
                    print(f"✅ [TEST_ISOLATION] 搜索参数缓存Key隔离正确")
                else:
                    print(f"❌ [TEST_ISOLATION] 搜索参数缓存Key隔离失败")

        except Exception as e:
            print(f"❌ [TEST_ISOLATION] 搜索参数测试异常: {e}")

    def test_performance_summary(self):
        """性能测试总结"""
        print("\n📊 [SUMMARY] 性能测试总结")
        print("-" * 60)

        # 连续测试技术广场列表性能
        url = f"{self.base_url}/api/v2/tech_square/documents"
        params = {"page": 1, "size": 10}

        times = []
        cache_hits = []

        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(url, params=params)
                request_time = (time.time() - start_time) * 1000
                times.append(request_time)

                if response.status_code == 200:
                    result = response.json()
                    cache_info = result.get('cache_info', {})
                    cache_hits.append(cache_info.get('cached', False))
                    print(
                        f"🔄 [SUMMARY] 第{i + 1}次请求: {request_time:.2f}ms, 缓存{'命中' if cache_info.get('cached') else '未命中'}")

            except Exception as e:
                print(f"❌ [SUMMARY] 第{i + 1}次请求异常: {e}")

            time.sleep(0.5)  # 间隔0.5秒

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            cache_hit_rate = sum(cache_hits) / len(cache_hits) * 100

            print(f"\n📈 [SUMMARY] 性能统计:")
            print(f"📈 [SUMMARY] 平均响应时间: {avg_time:.2f}ms")
            print(f"📈 [SUMMARY] 最快响应时间: {min_time:.2f}ms")
            print(f"📈 [SUMMARY] 最慢响应时间: {max_time:.2f}ms")
            print(f"📈 [SUMMARY] 缓存命中率: {cache_hit_rate:.1f}%")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 [TEST] 开始执行所有文档列表缓存测试")

        # 1. 用户登录
        if not self.login():
            print("❌ [TEST] 登录失败，部分测试将跳过")

        # 2. 技术广场文档列表缓存测试
        self.test_tech_square_list_cache()

        # 3. 个人文档列表缓存测试
        self.test_user_document_list_cache()

        # 4. 缓存隔离测试
        self.test_cache_isolation()

        # 5. 性能测试总结
        self.test_performance_summary()

        print("\n🎉 [TEST] 所有测试完成!")
        print("=" * 80)


if __name__ == "__main__":
    # 运行测试
    tester = DocumentListCacheTest()
    tester.run_all_tests()