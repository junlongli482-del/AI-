# app/core/ai_client.py
import requests
import json
import os
from typing import Optional, Dict, Any
from app.core.config import settings


class AIClient:
    """AI客户端，基于你提供的AI调用代码"""

    def __init__(self, api_url: str = None, api_key: str = None):
        # 使用传入参数或默认配置
        self.api_url = api_url or "http://127.0.0.1:8888/v1/chat-messages"
        self.upload_url = api_url.replace("chat-messages",
                                          "files/upload") if api_url else "http://127.0.0.1:8888/v1/files/upload"
        self.api_key = api_key or "app-JxcTVFGIpdo7gWhLaSoSAVTq"
        self.user_id = "system-md-editor"  # 系统用户ID

    def chat_with_ai(self, query: str, file_ids: Optional[list] = None, file_types: Optional[list] = None) -> Optional[
        str]:
        """
        与AI对话，基于你的原始代码改造
        """
        # 准备请求数据
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "conversation_id": "",
            "user": self.user_id,
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30  # 添加超时
            )

            # 处理响应
            if response.status_code == 200:
                response_data = response.json()
                answer = response_data.get("answer", "")
                return answer
            else:
                print(f"AI请求失败，状态码: {response.status_code}")
                print("错误信息:", response.text)
                return None

        except Exception as e:
            print(f"AI请求异常: {e}")
            return None

    def optimize_markdown(self, content: str, optimization_type: str = "general") -> Optional[str]:
        """
        优化Markdown内容
        """
        # 根据优化类型构建不同的提示词
        prompts = {
            "general": "请优化以下Markdown文档，保持原有结构和格式，提升表达质量、逻辑清晰度和可读性：",
            "grammar": "请检查并修正以下Markdown文档中的语法错误、拼写错误和表达问题，保持原有格式：",
            "structure": "请优化以下Markdown文档的结构和层次，使其更加清晰有序，保持原有内容：",
            "expand": "请在保持原有结构的基础上，适当扩展以下Markdown文档的内容，使其更加详细和完整："
        }

        prompt = prompts.get(optimization_type, prompts["general"])
        query = f"{prompt}\n\n{content}"

        return self.chat_with_ai(query)


# 创建默认AI客户端实例
default_ai_client = AIClient()