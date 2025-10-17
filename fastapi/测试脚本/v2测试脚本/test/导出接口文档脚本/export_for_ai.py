# 创建 export_for_ai.py
import requests
import json
from datetime import datetime


def export_api_docs_for_ai():
    """导出给AI看的API文档"""

    print("🤖 正在导出给AI的API文档...")

    try:
        # 获取完整的OpenAPI规范
        response = requests.get('http://localhost:8100/openapi.json')
        response.raise_for_status()
        api_spec = response.json()

        # 添加一些AI友好的元信息
        enhanced_spec = {
            "ai_readme": {
                "purpose": "FastAPI文档管理系统的完整API规范",
                "base_url": "http://localhost:8100",
                "auth_type": "Bearer Token",
                "test_account": {
                    "username": "abc",
                    "password": "ljl18420"
                },
                "export_time": datetime.now().isoformat(),
                "total_endpoints": len([
                    path for path_methods in api_spec['paths'].values()
                    for path in path_methods.keys()
                ]),
                "notes": [
                    "所有需要认证的接口都使用 Authorization: Bearer <token>",
                    "登录接口返回access_token，用于后续API调用",
                    "文件上传使用multipart/form-data格式",
                    "分页查询使用page和size参数",
                    "错误响应统一返回{detail: '错误信息'}格式"
                ]
            },
            **api_spec
        }

        # 保存为AI友好的文件名
        filename = 'fastapi_complete_api_spec.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(enhanced_spec, f, indent=2, ensure_ascii=False)

        print(f"✅ API文档已导出: {filename}")
        print(f"📊 包含 {enhanced_spec['ai_readme']['total_endpoints']} 个接口")
        print(f"📄 文件大小: {len(json.dumps(enhanced_spec))} 字符")
        print("\n🎯 使用说明:")
        print("1. 将此文件发送给AI")
        print("2. 告诉AI这是完整的API规范文档")
        print("3. AI可以基于此文档进行前端开发")

    except Exception as e:
        print(f"❌ 导出失败: {e}")


if __name__ == "__main__":
    export_api_docs_for_ai()