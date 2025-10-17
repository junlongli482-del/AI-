"""
Document Manager 模块清理+测试脚本
使用方法：python test_document_manager_clean.py
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8100"

def get_fresh_token():
    """获取新的token"""
    login_data = {
        "username_or_email": "abc",
        "password": "ljl18420"
    }

    response = requests.post(f"{BASE_URL}/api/v1/user_auth/login", json=login_data)
    if response.status_code == 200:
        result = response.json()
        return result["access_token"]
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def print_test_result(test_name, response):
    """打印测试结果"""
    print(f"\n{'=' * 50}")
    print(f"🧪 测试: {test_name}")
    print(f"状态码: {response.status_code}")

    try:
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    except:
        print(f"响应: {response.text}")
        return None

def cleanup_existing_data(headers):
    """清理现有测试数据"""
    print("🧹 开始清理现有测试数据...")

    # 1. 获取所有文档并删除
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/documents?page=1&page_size=100", headers=headers)
    if response.status_code == 200:
        docs = response.json()["documents"]
        for doc in docs:
            delete_response = requests.delete(f"{BASE_URL}/api/v2/document_manager/documents/{doc['id']}", headers=headers)
            if delete_response.status_code == 200:
                print(f"✅ 删除文档: {doc['title']}")
            else:
                print(f"❌ 删除文档失败: {doc['title']}")

    # 2. 获取文件夹树并删除（从子到父）
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/folders/tree", headers=headers)
    if response.status_code == 200:
        folders = response.json()

        # 收集所有文件夹ID（深度优先，子文件夹在前）
        def collect_folder_ids(folder_list, ids_list):
            for folder in folder_list:
                # 先收集子文件夹
                if folder.get("children"):
                    collect_folder_ids(folder["children"], ids_list)
                # 再收集当前文件夹
                ids_list.append(folder["id"])

        folder_ids = []
        collect_folder_ids(folders, folder_ids)

        # 删除文件夹
        for folder_id in folder_ids:
            delete_response = requests.delete(f"{BASE_URL}/api/v2/document_manager/folders/{folder_id}", headers=headers)
            if delete_response.status_code == 200:
                print(f"✅ 删除文件夹ID: {folder_id}")
            else:
                print(f"❌ 删除文件夹失败ID: {folder_id}")

    print("🧹 清理完成！")

def test_document_manager():
    """完整测试流程"""
    print("🚀 开始测试 Document Manager 模块")

    # 0. 获取新token
    print("\n" + "=" * 60)
    print("第零步：获取新的认证token")
    token = get_fresh_token()
    if not token:
        print("❌ 无法获取token，测试终止")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"✅ 获取到新token: {token[:20]}...")

    # 0.5. 清理现有数据
    cleanup_existing_data(headers)

    # 1. 测试模块健康检查
    print("\n" + "=" * 60)
    print("第一步：模块健康检查")
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/test")
    print_test_result("模块健康检查", response)

    # 2. 测试获取统计信息（清理后应该为0）
    print("\n" + "=" * 60)
    print("第二步：获取用户统计信息（清理后）")
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/stats", headers=headers)
    stats = print_test_result("获取统计信息", response)

    # 3. 测试创建文件夹
    print("\n" + "=" * 60)
    print("第三步：创建文件夹")

    # 创建根文件夹
    folder_data = {
        "name": "测试技术文档",
        "parent_id": None
    }
    response = requests.post(f"{BASE_URL}/api/v2/document_manager/folders",
                           headers=headers, json=folder_data)
    root_folder = print_test_result("创建根文件夹", response)

    root_folder_id = None
    sub_folder_id = None

    if root_folder and response.status_code == 200:
        root_folder_id = root_folder["id"]

        # 创建子文件夹
        subfolder_data = {
            "name": "Python测试笔记",
            "parent_id": root_folder_id
        }
        response = requests.post(f"{BASE_URL}/api/v2/document_manager/folders",
                               headers=headers, json=subfolder_data)
        sub_folder = print_test_result("创建子文件夹", response)

        if sub_folder and response.status_code == 200:
            sub_folder_id = sub_folder["id"]

    # 4. 测试获取文件夹树
    print("\n" + "=" * 60)
    print("第四步：获取文件夹树")
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/folders/tree", headers=headers)
    folder_tree = print_test_result("获取文件夹树", response)

    # 5. 测试创建文档
    print("\n" + "=" * 60)
    print("第五步：创建文档")

    root_doc_id = None
    sub_doc_id = None

    # 在根目录创建文档
    doc_data = {
        "title": "测试FastAPI指南",
        "content": "# 测试FastAPI指南\n\n这是一个测试文档。\n\n## 内容\n- 测试功能\n- 验证接口",
        "summary": "这是一份测试用的FastAPI指南",
        "folder_id": None,
        "file_type": "md"
    }
    response = requests.post(f"{BASE_URL}/api/v2/document_manager/documents",
                           headers=headers, json=doc_data)
    root_doc = print_test_result("在根目录创建文档", response)

    if root_doc and response.status_code == 200:
        root_doc_id = root_doc["id"]

    # 在子文件夹创建文档
    if sub_folder_id:
        doc_data2 = {
            "title": "测试Python语法",
            "content": "# 测试Python语法\n\n这是测试内容。\n\n```python\nprint('Hello Test!')\n```",
            "summary": "Python测试语法文档",
            "folder_id": sub_folder_id,
            "file_type": "md"
        }
        response = requests.post(f"{BASE_URL}/api/v2/document_manager/documents",
                               headers=headers, json=doc_data2)
        sub_doc = print_test_result("在子文件夹创建文档", response)

        if sub_doc and response.status_code == 200:
            sub_doc_id = sub_doc["id"]

    # 6. 测试获取文档列表
    print("\n" + "=" * 60)
    print("第六步：获取文档列表")

    # 获取所有文档
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/documents?page=1&page_size=10",
                          headers=headers)
    all_docs = print_test_result("获取所有文档", response)

    # 获取根目录文档
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/documents?folder_id=0&page=1&page_size=10",
                          headers=headers)
    root_docs = print_test_result("获取根目录文档", response)

    # 获取子文件夹文档
    if sub_folder_id:
        response = requests.get(f"{BASE_URL}/api/v2/document_manager/documents?folder_id={sub_folder_id}&page=1&page_size=10",
                              headers=headers)
        sub_docs = print_test_result("获取子文件夹文档", response)

    # 7. 测试获取文档详情
    print("\n" + "=" * 60)
    print("第七步：获取文档详情")

    if root_doc_id:
        response = requests.get(f"{BASE_URL}/api/v2/document_manager/documents/{root_doc_id}",
                              headers=headers)
        doc_detail = print_test_result("获取文档详情", response)

    # 8. 测试更新文档
    print("\n" + "=" * 60)
    print("第八步：更新文档")

    if root_doc_id:
        update_data = {
            "title": "测试FastAPI指南（已更新）",
            "content": "# 测试FastAPI指南（已更新）\n\n这是更新后的测试文档。\n\n## 新增内容\n- 更新测试\n- 验证修改功能",
            "summary": "这是更新后的测试FastAPI指南"
        }
        response = requests.put(f"{BASE_URL}/api/v2/document_manager/documents/{root_doc_id}",
                              headers=headers, json=update_data)
        updated_doc = print_test_result("更新文档", response)

    # 9. 测试最终统计
    print("\n" + "=" * 60)
    print("第九步：查看最终统计")
    response = requests.get(f"{BASE_URL}/api/v2/document_manager/stats", headers=headers)
    final_stats = print_test_result("最终统计信息", response)

    # 10. 清理测试数据
    print("\n" + "=" * 60)
    print("第十步：清理测试数据")

    cleanup = input("\n是否要清理本次测试数据？(y/n): ").lower().strip()

    if cleanup == 'y':
        cleanup_existing_data(headers)

        # 最终统计
        response = requests.get(f"{BASE_URL}/api/v2/document_manager/stats", headers=headers)
        print_test_result("清理后统计", response)

    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_document_manager()