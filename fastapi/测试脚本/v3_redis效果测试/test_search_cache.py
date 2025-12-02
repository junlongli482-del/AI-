"""
搜索结果缓存测试脚本
测试搜索功能的缓存优化
"""

import requests
import json
from datetime import datetime
import urllib.parse

# 配置
BASE_URL = "http://localhost:8100/api/v2/tech_square"

def test_search_cache():
    """测试搜索缓存功能"""
    print("🔍 测试搜索结果缓存")
    print("=" * 50)

    # 使用确实存在的关键词进行测试
    test_cases = [
        {"keyword": "00", "page": 1, "size": 10, "file_type": None},
        {"keyword": "10", "page": 1, "size": 5, "file_type": None},
        {"keyword": "AI", "page": 1, "size": 10, "file_type": "md"},
        {"keyword": "模块", "page": 1, "size": 20, "file_type": None},
        {"keyword": "计划", "page": 1, "size": 15, "file_type": None},
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n📊 测试用例 {i}: {case}")

        # 构建URL
        params = {
            "keyword": case["keyword"],
            "page": case["page"],
            "size": case["size"]
        }
        if case["file_type"]:
            params["file_type"] = case["file_type"]

        url = f"{BASE_URL}/search?" + "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])

        # 第一次请求（缓存未命中）
        print("第一次请求（预期缓存未命中）:")
        response1 = requests.get(url)
        print(f"状态码: {response1.status_code}")

        if response1.status_code == 200:
            data1 = response1.json()
            print(f"搜索结果: 当前页{len(data1.get('documents', []))}条, 总计{data1.get('total', 0)}条")
            cache_info1 = data1.get('cache_info', {})
            print(f"缓存状态: {cache_info1}")

            # 第二次请求（缓存命中）
            print("\n第二次请求（预期缓存命中）:")
            response2 = requests.get(url)
            print(f"状态码: {response2.status_code}")

            if response2.status_code == 200:
                data2 = response2.json()
                print(f"搜索结果: 当前页{len(data2.get('documents', []))}条, 总计{data2.get('total', 0)}条")
                cache_info2 = data2.get('cache_info', {})
                print(f"缓存状态: {cache_info2}")

                # 验证缓存命中
                if cache_info2.get('cached'):
                    print("✅ 缓存命中测试通过")
                else:
                    print("❌ 缓存命中测试失败")

                # 验证结果一致性
                if data1.get('total') == data2.get('total'):
                    print("✅ 结果一致性测试通过")
                else:
                    print("❌ 结果一致性测试失败")
            else:
                print(f"❌ 第二次请求失败: {response2.text}")
        else:
            print(f"❌ 第一次请求失败: {response1.text}")

def test_search_key_isolation():
    """测试搜索缓存Key隔离"""
    print("\n🔑 测试搜索缓存Key隔离")
    print("=" * 50)

    # 使用存在的关键词测试相同关键词不同参数的缓存隔离
    base_params = {"keyword": "AI", "page": 1, "size": 10}

    test_variations = [
        {**base_params},  # 基础参数
        {**base_params, "size": 5},  # 不同size
        {**base_params, "page": 2},  # 不同page
        {**base_params, "file_type": "md"},  # 不同file_type
    ]

    for i, params in enumerate(test_variations, 1):
        print(f"\n🔍 变体 {i}: {params}")

        url = f"{BASE_URL}/search?" + "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])

        # 两次请求验证缓存
        response1 = requests.get(url)
        response2 = requests.get(url)

        if response1.status_code == 200 and response2.status_code == 200:
            cache_info1 = response1.json().get('cache_info', {})
            cache_info2 = response2.json().get('cache_info', {})

            print(f"第一次: 缓存={cache_info1.get('cached', False)}")
            print(f"第二次: 缓存={cache_info2.get('cached', False)}")

            if not cache_info1.get('cached') and cache_info2.get('cached'):
                print("✅ 缓存Key隔离正常")
            else:
                print("❌ 缓存Key隔离异常")

def test_chinese_keyword_search():
    """测试中文关键词搜索缓存"""
    print("\n🇨🇳 测试中文关键词搜索缓存")
    print("=" * 50)

    # 使用确实存在的中文关键词
    chinese_keywords = ["模块", "计划"]

    for keyword in chinese_keywords:
        print(f"\n🔍 测试中文关键词: '{keyword}'")

        url = f"{BASE_URL}/search?keyword={urllib.parse.quote(keyword)}&page=1&size=10"

        # 两次请求验证缓存
        response1 = requests.get(url)
        response2 = requests.get(url)

        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()

            cache_info1 = data1.get('cache_info', {})
            cache_info2 = data2.get('cache_info', {})

            print(f"第一次: 缓存={cache_info1.get('cached', False)}, 结果={len(data1.get('documents', []))}条")
            print(f"第二次: 缓存={cache_info2.get('cached', False)}, 结果={len(data2.get('documents', []))}条")

            if cache_info2.get('cached'):
                print("✅ 中文关键词缓存正常")
            else:
                print("❌ 中文关键词缓存失败")

def test_numeric_keyword_search():
    """测试数字关键词搜索缓存"""
    print("\n🔢 测试数字关键词搜索缓存")
    print("=" * 50)

    # 使用确实存在的数字关键词
    numeric_keywords = ["00", "10"]

    for keyword in numeric_keywords:
        print(f"\n🔍 测试数字关键词: '{keyword}'")

        url = f"{BASE_URL}/search?keyword={keyword}&page=1&size=10"

        # 两次请求验证缓存
        response1 = requests.get(url)
        response2 = requests.get(url)

        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()

            cache_info1 = data1.get('cache_info', {})
            cache_info2 = data2.get('cache_info', {})

            print(f"第一次: 缓存={cache_info1.get('cached', False)}, 结果={len(data1.get('documents', []))}条")
            print(f"第二次: 缓存={cache_info2.get('cached', False)}, 结果={len(data2.get('documents', []))}条")

            if cache_info2.get('cached'):
                print("✅ 数字关键词缓存正常")
            else:
                print("❌ 数字关键词缓存失败")

def test_performance_comparison():
    """测试性能对比"""
    print("\n⚡ 测试搜索缓存性能对比")
    print("=" * 50)

    import time

    # 使用一个存在的关键词进行性能测试
    test_keyword = "AI"
    url = f"{BASE_URL}/search?keyword={test_keyword}&page=1&size=10"

    print(f"🔍 性能测试关键词: '{test_keyword}'")

    # 第一次请求（缓存未命中）
    start_time = time.time()
    response1 = requests.get(url)
    first_request_time = (time.time() - start_time) * 1000

    if response1.status_code == 200:
        data1 = response1.json()
        print(f"第一次请求耗时: {first_request_time:.2f}ms")
        print(f"搜索结果: {len(data1.get('documents', []))}条")

        # 第二次请求（缓存命中）
        start_time = time.time()
        response2 = requests.get(url)
        second_request_time = (time.time() - start_time) * 1000

        if response2.status_code == 200:
            data2 = response2.json()
            print(f"第二次请求耗时: {second_request_time:.2f}ms")
            print(f"搜索结果: {len(data2.get('documents', []))}条")

            if first_request_time > 0 and second_request_time > 0:
                improvement = ((first_request_time - second_request_time) / first_request_time) * 100
                print(f"性能提升: {improvement:.1f}%")

                if improvement > 0:
                    print("✅ 性能提升测试通过")
                else:
                    print("❌ 性能提升测试失败")

def main():
    """主测试函数"""
    print("🧪 搜索结果缓存功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试地址: {BASE_URL}")
    print(f"测试关键词: 00, 10, AI, 模块, 计划")

    try:
        # 测试基础搜索缓存
        test_search_cache()

        # 测试缓存Key隔离
        test_search_key_isolation()

        # 测试中文关键词
        test_chinese_keyword_search()

        # 测试数字关键词
        test_numeric_keyword_search()

        # 测试性能对比
        test_performance_comparison()

        print("\n🎉 所有测试完成!")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()