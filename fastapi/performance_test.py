#!/usr/bin/env python3
"""
性能测试脚本
"""
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics


def test_single_request(url):
    """测试单个请求"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()

        if response.status_code == 200:
            return end_time - start_time
        else:
            return None
    except:
        return None


def test_performance():
    """性能测试主函数"""
    print("🧪 FastAPI性能测试")
    print("=" * 50)

    # 测试URL
    urls = [
        "http://localhost:8100/api/health",
        "http://localhost:8101/api/health",
        "http://localhost:8102/api/health",
        "http://localhost:8103/api/health"
    ]

    # 检查服务可用性
    available_urls = []
    for url in urls:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                available_urls.append(url)
                print(f"✅ {url} - 在线")
            else:
                print(f"❌ {url} - 离线")
        except:
            print(f"❌ {url} - 离线")

    if not available_urls:
        print("❌ 没有可用的服务")
        return

    print(f"\n📊 开始性能测试 (可用服务: {len(available_urls)}个)")

    # 并发测试
    test_cases = [
        {"threads": 1, "requests": 10, "name": "单线程测试"},
        {"threads": 5, "requests": 50, "name": "5线程并发"},
        {"threads": 10, "requests": 100, "name": "10线程并发"},
        {"threads": 20, "requests": 200, "name": "20线程并发"}
    ]

    for test_case in test_cases:
        print(f"\n🔄 {test_case['name']}...")

        start_time = time.time()
        response_times = []

        with ThreadPoolExecutor(max_workers=test_case['threads']) as executor:
            # 轮询使用可用的URL
            futures = []
            for i in range(test_case['requests']):
                url = available_urls[i % len(available_urls)]
                future = executor.submit(test_single_request, url)
                futures.append(future)

            # 收集结果
            for future in futures:
                result = future.result()
                if result is not None:
                    response_times.append(result)

        end_time = time.time()

        # 统计结果
        if response_times:
            total_time = end_time - start_time
            success_rate = len(response_times) / test_case['requests'] * 100
            avg_response = statistics.mean(response_times) * 1000  # 转换为毫秒
            min_response = min(response_times) * 1000
            max_response = max(response_times) * 1000
            rps = len(response_times) / total_time

            print(f"   📈 总耗时: {total_time:.2f}s")
            print(f"   📈 成功率: {success_rate:.1f}%")
            print(f"   📈 平均响应: {avg_response:.1f}ms")
            print(f"   📈 最快响应: {min_response:.1f}ms")
            print(f"   📈 最慢响应: {max_response:.1f}ms")
            print(f"   📈 QPS: {rps:.1f} req/s")
        else:
            print("   ❌ 测试失败")


if __name__ == "__main__":
    test_performance()