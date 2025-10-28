"""
文档下载功能测试脚本
"""
import requests
import json


class DocumentDownloadTester:
    def __init__(self):
        self.base_url = "http://localhost:8100/api/v2/document_manager"
        self.token = None
        self.test_document_id = None

    def login(self):
        """登录获取token"""
        login_url = "http://localhost:8100/api/v1/user_auth/login"
        login_data = {
            "username_or_email": "abc",
            "password": "ljl18420"
        }

        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            print("✅ 登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def test_file_info(self):
        """测试文件信息接口"""
        print("\n📋 测试文件信息接口...")

        # 先获取文档列表找到有文件的文档
        response = requests.get(
            f"{self.base_url}/documents",
            headers=self.get_headers()
        )

        if response.status_code == 200:
            docs = response.json()["documents"]
            pdf_doc = None

            for doc in docs:
                if doc["file_type"] == "pdf":
                    pdf_doc = doc
                    break

            if pdf_doc:
                self.test_document_id = pdf_doc["id"]
                print(f"找到PDF文档: {pdf_doc['title']} (ID: {pdf_doc['id']})")

                # 测试文件信息
                info_response = requests.get(
                    f"{self.base_url}/documents/{pdf_doc['id']}/info",
                    headers=self.get_headers()
                )

                if info_response.status_code == 200:
                    info = info_response.json()
                    print(f"✅ 文件信息获取成功:")
                    print(f"   - 文件类型: {info['file_type']}")
                    print(f"   - 文件大小: {info['file_size']} bytes")
                    print(f"   - 文件存在: {info['file_exists']}")
                    print(f"   - MIME类型: {info.get('mime_type', 'N/A')}")
                    return True
                else:
                    print(f"❌ 文件信息获取失败: {info_response.text}")
            else:
                print("⚠️ 没有找到PDF文档")

        return False

    def test_download_modes(self):
        """测试不同下载模式"""
        if not self.test_document_id:
            print("⚠️ 没有可测试的文档ID")
            return False

        print(f"\n📥 测试文档下载功能 (ID: {self.test_document_id})...")

        # 测试下载模式
        print("测试下载模式...")
        download_response = requests.get(
            f"{self.base_url}/documents/{self.test_document_id}/download",
            headers=self.get_headers()
        )

        if download_response.status_code == 200:
            print(f"✅ 下载模式测试成功")
            print(f"   - Content-Type: {download_response.headers.get('content-type')}")
            print(f"   - Content-Length: {download_response.headers.get('content-length')}")
            print(f"   - Content-Disposition: {download_response.headers.get('content-disposition')}")
        else:
            print(f"❌ 下载模式测试失败: {download_response.text}")
            return False

        # 测试预览模式
        print("测试预览模式...")
        preview_response = requests.get(
            f"{self.base_url}/documents/{self.test_document_id}/download?preview=true",
            headers=self.get_headers()
        )

        if preview_response.status_code == 200:
            print(f"✅ 预览模式测试成功")
            print(f"   - Content-Disposition: {preview_response.headers.get('content-disposition')}")
        else:
            print(f"❌ 预览模式测试失败: {preview_response.text}")
            return False

        return True

    def test_stream_mode(self):
        """测试流式传输"""
        if not self.test_document_id:
            return False

        print(f"\n🌊 测试流式传输功能...")

        stream_response = requests.get(
            f"{self.base_url}/documents/{self.test_document_id}/stream",
            headers=self.get_headers(),
            stream=True
        )

        if stream_response.status_code == 200:
            print(f"✅ 流式传输测试成功")
            print(f"   - Content-Type: {stream_response.headers.get('content-type')}")
            print(f"   - Accept-Ranges: {stream_response.headers.get('accept-ranges')}")

            # 读取部分数据验证
            chunk_count = 0
            for chunk in stream_response.iter_content(chunk_size=1024):
                chunk_count += 1
                if chunk_count >= 3:  # 只读取前3个chunk
                    break

            print(f"   - 成功读取 {chunk_count} 个数据块")
            return True
        else:
            print(f"❌ 流式传输测试失败: {stream_response.text}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始文档下载功能测试")
        print("=" * 50)

        if not self.login():
            return

        tests = [
            ("文件信息接口", self.test_file_info),
            ("下载模式测试", self.test_download_modes),
            ("流式传输测试", self.test_stream_mode),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - 通过")
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {str(e)}")

        print("\n" + "=" * 50)
        print(f"📊 测试完成: {passed}/{total} 通过")

        if self.test_document_id:
            print(f"\n🔗 前端测试链接:")
            print(f"预览: http://localhost:8100/api/v2/document_manager/documents/{self.test_document_id}/stream")
            print(f"下载: http://localhost:8100/api/v2/document_manager/documents/{self.test_document_id}/download")


if __name__ == "__main__":
    tester = DocumentDownloadTester()
    tester.run_all_tests()