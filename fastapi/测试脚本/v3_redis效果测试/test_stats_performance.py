"""
统计接口性能测试脚本
功能：测试stats接口的性能，为缓存优化建立基准
"""
import requests
import time
import json
from typing import List, Dict

# 测试配置
BASE_URL = "http://localhost:8100/api"
TEST_USER = {
    "username": "abc",
    "password": "ljl18420"
}


class StatsPerformanceTester:
    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def login(self) -> bool:
        """登录获取token"""
        print("🔐 正在登录...")

        try:
            response = self.session.post(
                f"{BASE_URL}/v1/user_auth/login",
                json={
                    "username_or_email": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                print("✅ 登录成功")
                return True
            else:
                print(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False

    def test_stats_single(self) -> Dict:
        """单次测试stats接口"""
        start_time = time.time()

        try:
            response = self.session.get(f"{BASE_URL}/v2/document_manager/stats")
            request_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "request_time_ms": round(request_time, 2),
                    "total_documents": data.get("total_documents", 0),
                    "total_folders": data.get("total_folders", 0),
                    "debug_info": data.get("_debug_info", {}),
                    "response_size": len(response.text)
                }
            else:
                return {
                    "success": False,
                    "request_time_ms": round(request_time, 2),
                    "error": f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            request_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "request_time_ms": round(request_time, 2),
                "error": str(e)
            }

    def test_stats_multiple(self, count: int = 5) -> List[Dict]:
        """多次测试stats接口"""
        print(f"🧪 开始进行{count}次性能测试...")
        results = []

        for i in range(count):
            print(f"📊 第{i + 1}次测试...")
            result = self.test_stats_single()
            results.append(result)

            if result["success"]:
                print(f"✅ 测试{i + 1}完成: {result['request_time_ms']}ms")
            else:
                print(f"❌ 测试{i + 1}失败: {result['error']}")

            # 间隔一秒，避免请求过快
            if i < count - 1:
                time.sleep(1)

        return results

    def analyze_results(self, results: List[Dict]):
        """分析测试结果"""
        print("\n📈 性能分析报告")
        print("=" * 50)

        successful_results = [r for r in results if r["success"]]

        if not successful_results:
            print("❌ 没有成功的测试结果")
            return

        # 请求时间分析
        request_times = [r["request_time_ms"] for r in successful_results]
        avg_request_time = sum(request_times) / len(request_times)
        min_request_time = min(request_times)
        max_request_time = max(request_times)

        print(f"🔍 总测试次数: {len(results)}")
        print(f"✅ 成功次数: {len(successful_results)}")
        print(f"❌ 失败次数: {len(results) - len(successful_results)}")
        print(f"📊 成功率: {len(successful_results) / len(results) * 100:.1f}%")
        print()
        print("⚡ 请求时间分析:")
        print(f"   平均: {avg_request_time:.2f}ms")
        print(f"   最快: {min_request_time:.2f}ms")
        print(f"   最慢: {max_request_time:.2f}ms")
        print(f"   差异: {max_request_time - min_request_time:.2f}ms")

        # 数据库查询时间分析
        if successful_results[0].get("debug_info", {}).get("query_performance"):
            print("\n🗄️ 数据库查询时间分析:")

            db_times = []
            for result in successful_results:
                perf = result["debug_info"]["query_performance"]
                total_db = perf["total_docs_ms"] + perf["status_stats_ms"] + perf["total_folders_ms"]
                db_times.append({
                    "total_docs": perf["total_docs_ms"],
                    "status_stats": perf["status_stats_ms"],
                    "total_folders": perf["total_folders_ms"],
                    "total_db": total_db
                })

            avg_total_docs = sum(d["total_docs"] for d in db_times) / len(db_times)
            avg_status_stats = sum(d["status_stats"] for d in db_times) / len(db_times)
            avg_total_folders = sum(d["total_folders"] for d in db_times) / len(db_times)
            avg_total_db = sum(d["total_db"] for d in db_times) / len(db_times)

            print(f"   总文档查询: {avg_total_docs:.2f}ms")
            print(f"   状态统计查询: {avg_status_stats:.2f}ms")
            print(f"   文件夹查询: {avg_total_folders:.2f}ms")
            print(f"   数据库总耗时: {avg_total_db:.2f}ms")
            print(f"   数据库占比: {avg_total_db / avg_request_time * 100:.1f}%")

        # 数据统计
        if successful_results:
            sample = successful_results[0]
            print(f"\n📊 数据统计:")
            print(f"   总文档数: {sample['total_documents']}")
            print(f"   总文件夹数: {sample['total_folders']}")
            print(f"   响应大小: {sample['response_size']} bytes")


def main():
    """主函数"""
    print("🚀 Stats接口性能测试工具")
    print("=" * 50)

    tester = StatsPerformanceTester()

    # 登录
    if not tester.login():
        return

    # 执行测试
    results = tester.test_stats_multiple(5)

    # 分析结果
    tester.analyze_results(results)

    print("\n🎯 测试完成!")
    print("💡 提示: 观察后端控制台的详细调试信息")


if __name__ == "__main__":
    main()