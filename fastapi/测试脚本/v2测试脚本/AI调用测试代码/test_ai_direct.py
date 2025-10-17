# test_ai_direct.py
import requests
import json
import time


def test_real_ai_service():
    """测试真实的AI服务"""
    api_url = "http://127.0.0.1:8888/v1/chat-messages"
    api_key = "app-Tsm3DbgdIXiaFZMKBuNR7IO9"

    payload = {
        "inputs": {},
        "query": "你好，请回复一个简单的测试消息",
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "test_user",
        "files": []
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print("🧪 测试真实AI服务...")
    print(f"开始时间: {time.strftime('%H:%M:%S')}")

    start_time = time.time()

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=120  # 2分钟超时
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"结束时间: {time.strftime('%H:%M:%S')}")
        print(f"实际耗时: {duration:.1f}秒")
        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ AI服务连接成功")
            data = response.json()
            print("📄 完整响应结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            answer = data.get("answer", "")
            print(f"\n🤖 AI回复内容: {answer}")

        else:
            print("❌ AI服务调用失败")
            print(f"响应内容: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ 请求超时（超过2分钟）")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到AI服务")
    except Exception as e:
        print(f"❌ 请求异常: {e}")


if __name__ == "__main__":
    test_real_ai_service()