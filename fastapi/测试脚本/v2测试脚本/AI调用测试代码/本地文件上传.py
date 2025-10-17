import requests
import json
import os
import mimetypes

api_url = "http://127.0.0.1:8888/v1/chat-messages"
upload_url = "http://127.0.0.1:8888/v1/files/upload"
api_key = "app-JxcTVFGIpdo7gWhLaSoSAVTq"
user_id = "abc-123"


def get_file_type(filename):
    """根据文件扩展名确定文件类型"""
    extension = os.path.splitext(filename)[1].lower().replace('.', '')

    # 文档类型
    document_extensions = ['txt', 'md', 'markdown', 'pdf', 'html', 'xlsx', 'xls', 'docx', 'csv', 'eml', 'msg', 'pptx',
                           'ppt', 'xml', 'epub']
    # 图片类型
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
    # 音频类型
    audio_extensions = ['mp3', 'm4a', 'wav', 'webm', 'amr']
    # 视频类型
    video_extensions = ['mp4', 'mov', 'mpeg', 'mpga']

    if extension in document_extensions:
        return 'document'
    elif extension in image_extensions:
        return 'image'
    elif extension in audio_extensions:
        return 'audio'
    elif extension in video_extensions:
        return 'video'
    else:
        return 'custom'


def upload_file(file_path):
    """
    上传本地文件到服务器
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None

    try:
        filename = os.path.basename(file_path)
        file_type = get_file_type(filename)

        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        # 准备上传文件
        files = {
            'file': (filename, open(file_path, 'rb'), mime_type)
        }
        data = {
            'user': user_id
        }

        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        print(f"正在上传文件: {file_path}")
        print(f"文件类型: {file_type}, MIME类型: {mime_type}")

        response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            data=data
        )

        # 修复：201状态码也表示成功（创建成功）
        if response.status_code in [200, 201]:
            upload_data = response.json()
            file_id = upload_data.get("id")
            print(f"✅ 文件上传成功! 文件ID: {file_id}")
            print(f"文件名: {upload_data.get('name')}")
            print(f"文件大小: {upload_data.get('size')} bytes")
            return file_id
        else:
            print(f"❌ 文件上传失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None

    except Exception as e:
        print(f"上传文件时发生错误: {e}")
        return None
    finally:
        if 'files' in locals() and files['file'][1]:
            files['file'][1].close()


def chat_with_file(query, file_ids=None, file_types=None):
    """
    与AI对话，可以包含文件
    """
    # 准备请求数据
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": user_id,
        "files": []
    }

    # 如果有文件ID，添加到files数组中
    if file_ids and file_types:
        for file_id, file_type in zip(file_ids, file_types):
            payload["files"].append({
                "type": file_type,
                "transfer_method": "local_file",
                "upload_file_id": file_id
            })

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"\n📤 发送请求到AI...")
    print(f"问题: {query}")
    if file_ids:
        print(f"使用文件ID: {file_ids}")

    # 发送请求
    response = requests.post(
        api_url,
        headers=headers,
        data=json.dumps(payload)
    )

    # 处理响应
    if response.status_code == 200:
        print("✅ 请求成功！")
        response_data = response.json()
        answer = response_data.get("answer", "未找到回答")
        print("🤖 AI回复:", answer)
        return answer
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        print("错误信息:", response.text)
        return None


# 使用示例
if __name__ == "__main__":
    print("=" * 50)
    print("AI文件对话程序")
    print("=" * 50)

    # 1. 上传文件
    file_path = input("请输入要上传的文件路径（直接回车跳过文件上传）: ")
    file_ids = []
    file_types = []

    if file_path and file_path.strip():
        file_id = upload_file(file_path.strip())
        if file_id:
            file_ids.append(file_id)
            # 获取文件类型
            filename = os.path.basename(file_path.strip())
            file_type = get_file_type(filename)
            file_types.append(file_type)
            print(f"📝 检测到文件类型: {file_type}")

    # 2. 进行对话
    print("\n" + "=" * 50)
    print("开始对话（输入'退出'结束对话）")
    print("=" * 50)

    while True:
        query = input("\n💬 请输入你的问题: ")
        if query.lower() in ['退出', 'exit', 'quit']:
            print("👋 再见！")
            break

        if not query.strip():
            print("⚠️  问题不能为空，请重新输入")
            continue

        chat_with_file(query, file_ids if file_ids else None, file_types if file_types else None)