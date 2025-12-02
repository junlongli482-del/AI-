import requests
import time
import redis
import json


def test_redis_performance():
    print("🧪 测试Redis缓存性能...")

    # 先登录获取token
    login_response = requests.post("http://localhost:8100/api/v1/user_auth/login",
                                   json={"username_or_email": "abc", "password": "ljl18420"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 连接到Redis
    r = redis.Redis(host='localhost', port=6380, decode_responses=True)

    # 先清理测试缓存
    test_cache_key = "fastapi_docs:user:6"
    r.delete(test_cache_key)

    print(f"🔍 测试缓存键: {test_cache_key}")
    print("-" * 50)

    # 测试5次请求
    times = []
    cache_status = []  # 记录每次请求是否命中缓存

    for i in range(5):
        # 请求前检查缓存状态
        cached_before = r.exists(test_cache_key)

        start = time.time()
        response = requests.get("http://localhost:8100/api/v1/user_auth/me", headers=headers)
        elapsed = (time.time() - start) * 1000

        # 请求后检查缓存状态
        cached_after = r.exists(test_cache_key)

        times.append(elapsed)
        cache_hit = cached_before and response.status_code == 200
        cache_status.append(cache_hit)

        print(f"第{i + 1}次请求: {elapsed:.2f}ms | 缓存: {'命中' if cache_hit else '未命中'}")

        # 如果是第一次请求，显示写入的缓存内容
        if i == 0 and cached_after:
            cached_data = r.get(test_cache_key)
            if cached_data:
                try:
                    parsed_data = json.loads(cached_data)
                    print(f"   缓存内容: {parsed_data}")
                except:
                    print(f"   缓存内容: {cached_data}")

    print("-" * 50)

    # 性能分析
    if len(times) > 1:
        first_request = times[0]
        cached_requests = [time for i, time in enumerate(times[1:]) if cache_status[i + 1]]

        if cached_requests:
            avg_cached = sum(cached_requests) / len(cached_requests)
            improvement = ((first_request - avg_cached) / first_request) * 100
            print(f"📊 性能分析:")
            print(f"   首次请求(数据库): {first_request:.2f}ms")
            print(f"   缓存请求平均: {avg_cached:.2f}ms")
            print(f"   🚀 性能提升: {improvement:.1f}%")
        else:
            print("⚠️ 没有成功的缓存请求")

    # 验证缓存一致性
    print("\n🔍 验证缓存一致性:")
    cached_data = r.get(test_cache_key)
    if cached_data:
        cached_user = json.loads(cached_data)
        direct_response = requests.get("http://localhost:8100/api/v1/user_auth/me", headers=headers).json()

        print(f"   缓存数据: {cached_user}")
        print(f"   直接请求: {direct_response}")
        print(f"   数据一致: {cached_user == direct_response}")


def test_redis_direct_operations():
    print("\n" + "=" * 60)
    print("🔧 测试Redis直接操作性能...")

    r = redis.Redis(host='localhost', port=6380, decode_responses=True)

    # 测试Redis SET操作
    start = time.time()
    for i in range(100):
        r.set(f"test:key:{i}", json.dumps({"id": i, "name": f"user{i}"}))
    set_time = (time.time() - start) * 1000

    # 测试Redis GET操作
    start = time.time()
    for i in range(100):
        r.get(f"test:key:{i}")
    get_time = (time.time() - start) * 1000

    print(f"Redis SET 100次: {set_time:.2f}ms (平均 {set_time / 100:.2f}ms/次)")
    print(f"Redis GET 100次: {get_time:.2f}ms (平均 {get_time / 100:.2f}ms/次)")

    # 清理测试数据
    for i in range(100):
        r.delete(f"test:key:{i}")


if __name__ == "__main__":
    test_redis_performance()
    test_redis_direct_operations()