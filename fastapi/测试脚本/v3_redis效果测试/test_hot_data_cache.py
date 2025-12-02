"""
热门数据缓存测试脚本
测试热门文档和最新文档的缓存功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8100/api/v2/tech_square"


def test_hot_documents():
    """测试热门文档缓存"""
    print("🔥 测试热门文档缓存")
    print("=" * 50)

    # 测试不同的limit参数
    test_cases = [10, 5, 20]

    for limit in test_cases:
        print(f"\n📊 测试limit={limit}")

        # 第一次请求（缓存未命中）
        print("第一次请求（预期缓存未命中）:")
        response1 = requests.get(f"{BASE_URL}/hot-documents?limit={limit}")
        print(f"状态码: {response1.status_code}")

        if response1.status_code == 200:
            data1 = response1.json()
            print(f"文档数量: {len(data1.get('documents', []))}")
            cache_info1 = data1.get('cache_info', {})
            print(f"缓存状态: {cache_info1}")

            # 第二次请求（缓存命中）
            print("\n第二次请求（预期缓存命中）:")
            response2 = requests.get(f"{BASE_URL}/hot-documents?limit={limit}")
            print(f"状态码: {response2.status_code}")

            if response2.status_code == 200:
                data2 = response2.json()
                print(f"文档数量: {len(data2.get('documents', []))}")
                cache_info2 = data2.get('cache_info', {})
                print(f"缓存状态: {cache_info2}")

                # 验证缓存命中
                if cache_info2.get('cached'):
                    print("✅ 缓存命中测试通过")
                else:
                    print("❌ 缓存命中测试失败")
            else:
                print(f"❌ 第二次请求失败: {response2.text}")
        else:
            print(f"❌ 第一次请求失败: {response1.text}")


def test_latest_documents():
    """测试最新文档缓存"""
    print("\n📅 测试最新文档缓存")
    print("=" * 50)

    # 测试不同的limit参数
    test_cases = [10, 5, 15]

    for limit in test_cases:
        print(f"\n📊 测试limit={limit}")

        # 第一次请求（缓存未命中）
        print("第一次请求（预期缓存未命中）:")
        response1 = requests.get(f"{BASE_URL}/latest-documents?limit={limit}")
        print(f"状态码: {response1.status_code}")

        if response1.status_code == 200:
            data1 = response1.json()
            print(f"文档数量: {len(data1.get('documents', []))}")
            cache_info1 = data1.get('cache_info', {})
            print(f"缓存状态: {cache_info1}")

            # 第二次请求（缓存命中）
            print("\n第二次请求（预期缓存命中）:")
            response2 = requests.get(f"{BASE_URL}/latest-documents?limit={limit}")
            print(f"状态码: {response2.status_code}")

            if response2.status_code == 200:
                data2 = response2.json()
                print(f"文档数量: {len(data2.get('documents', []))}")
                cache_info2 = data2.get('cache_info', {})
                print(f"缓存状态: {cache_info2}")

                # 验证缓存命中
                if cache_info2.get('cached'):
                    print("✅ 缓存命中测试通过")
                else:
                    print("❌ 缓存命中测试失败")
            else:
                print(f"❌ 第二次请求失败: {response2.text}")
        else:
            print(f"❌ 第一次请求失败: {response1.text}")


def main():
    """主测试函数"""
    print("🧪 热门数据缓存功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试地址: {BASE_URL}")

    try:
        # 测试热门文档缓存
        test_hot_documents()

        # 测试最新文档缓存
        test_latest_documents()

        print("\n🎉 所有测试完成!")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")


if __name__ == "__main__":
    main()