"""
文件上传模块完整测试脚本 - 本地文件版本
功能：测试所有文件上传相关的API接口，支持使用本地文件
版本：v2.2 - 本地文件测试版（修复版）
"""

import requests
import json
import os
import tempfile
import time
from pathlib import Path

# 测试配置
BASE_URL = "http://localhost:8100"
TEST_USER = {
    "username": "abc",
    "password": "ljl18420"
}

# 本地文件配置 - 请修改为你的文件路径
LOCAL_FILES = {
    "md_file": r"C:\A_XM\xm_3\vue3-fastapi-mysql_v1.0\fastapi\文档\V1阶段开发文档\v1开发文档.md",  # 修改为你的MD文件路径
    "pdf_file": r"C:\Users\LJL\Desktop\静态心电第二页\24561_蒲玉莲_心电图报告.pdf",  # 修改为你的PDF文件路径
}


class FileUploadTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.temp_dir = None
        self.test_files = {}
        self.upload_results = {}
        self.use_local_files = False

    def log_success(self, message):
        print(f"✅ {message}")

    def log_error(self, message):
        print(f"❌ {message}")

    def log_info(self, message):
        print(f"ℹ️  {message}")

    def log_step(self, step):
        print(f"\n📋 {step}")
        print("-" * 50)

    def check_local_files(self):
        """检查本地文件是否存在"""
        self.log_step("检查本地文件")

        available_files = {}

        for file_type, file_path in LOCAL_FILES.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_success(f"{file_type}: {file_path} (大小: {file_size} 字节)")
                available_files[file_type] = file_path
            else:
                self.log_error(f"{file_type}: {file_path} - 文件不存在")

        if available_files:
            self.log_info(f"找到 {len(available_files)} 个本地文件")
            choice = input("\n是否使用本地文件进行测试？(y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                self.use_local_files = True
                self.test_files.update(available_files)
                return True

        self.log_info("将使用生成的测试文件")
        return False

    def setup_test_environment(self):
        """设置测试环境"""
        self.log_step("设置测试环境")

        # 1. 检查服务器连接
        self.log_info("检查服务器连接...")
        try:
            response = requests.get(f"{self.base_url}/api/v2/file_upload/test", timeout=5)
            if response.status_code == 200:
                self.log_success("服务器连接正常")
            else:
                raise Exception(f"服务器响应异常: {response.status_code}")
        except Exception as e:
            self.log_error(f"服务器连接失败: {str(e)}")
            raise

        # 2. 用户登录
        self.log_info("用户登录...")
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/user_auth/login",
                json={
                    "username_or_email": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.log_success(f"登录成功，Token获取成功")
                self.log_info(f"用户: {TEST_USER['username']}")
            else:
                self.log_error(f"登录失败，状态码: {response.status_code}")
                self.log_error(f"响应内容: {response.text}")
                raise Exception(f"登录失败: {response.text}")
        except Exception as e:
            self.log_error(f"登录过程出错: {str(e)}")
            raise

        # 3. 检查并选择测试文件
        if not self.check_local_files():
            self.log_info("创建测试文件...")
            self.create_test_files()

    def create_test_files(self):
        """创建测试文件"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="file_upload_test_")
        self.log_info(f"临时目录: {self.temp_dir}")

        # 1. 创建有效的MD文件
        md_content = """# 文件上传测试文档

这是一个用于测试文件上传功能的Markdown文档。

## 测试内容

### 基础功能测试
- 文件格式验证
- 文件大小检查
- 内容完整性验证

## 代码示例

```python
def test_file_upload():
    print("测试文件上传功能")
    return True
总结
这个测试文档用于验证文件上传模块的功能。
"""

        valid_md_file = os.path.join(self.temp_dir, "valid_test.md")
        with open(valid_md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        self.test_files['md_file'] = valid_md_file

        # 2. 创建有效的PDF文件
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000074 00000 n
0000000120 00000 n
trailer
<< /Size 4 /Root 1 0 R >>
startxref
179
%%EOF"""

        valid_pdf_file = os.path.join(self.temp_dir, "valid_test.pdf")
        with open(valid_pdf_file, 'wb') as f:
            f.write(pdf_content)
        self.test_files['pdf_file'] = valid_pdf_file

        # 3. 创建无效的PDF文件（用于验证测试）
        invalid_pdf_file = os.path.join(self.temp_dir, "invalid_test.pdf")
        with open(invalid_pdf_file, 'w', encoding='utf-8') as f:
            f.write("这不是一个PDF文件")
        self.test_files['invalid_pdf'] = invalid_pdf_file

        self.log_success(f"测试文件创建完成，共 {len(self.test_files)} 个文件")

    def get_headers(self):
        """获取请求头"""
        return {"Authorization": f"Bearer {self.token}"}

    def test_01_get_config(self):
        """测试1: 获取上传配置"""
        self.log_step("测试1: 获取上传配置")

        try:
            response = requests.get(
                f"{self.base_url}/api/v2/file_upload/config",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                config = response.json()
                self.log_success("配置获取成功")
                self.log_info(f"最大文件大小: {config['max_file_size_mb']}MB")
                self.log_info(f"支持格式: {config['allowed_extensions']}")
                return True
            else:
                self.log_error(f"配置获取失败: {response.text}")
                return False

        except Exception as e:
            self.log_error(f"配置获取异常: {str(e)}")
            return False

    def test_02_validate_files(self):
        """测试2: 文件验证功能"""
        self.log_step("测试2: 文件验证功能")

        # 根据是否使用本地文件调整测试用例
        if self.use_local_files:
            test_cases = []
            if 'md_file' in self.test_files:
                test_cases.append(("md_file", "本地MD文件", True))
            if 'pdf_file' in self.test_files:
                test_cases.append(("pdf_file", "本地PDF文件", True))
        else:
            test_cases = [
                ("md_file", "生成的MD文件", True),
                ("pdf_file", "生成的PDF文件", True),
                ("invalid_pdf", "无效PDF文件", False),
            ]

        success_count = 0

        for file_key, description, should_pass in test_cases:
            if file_key not in self.test_files:
                continue

            self.log_info(f"验证 {description}...")

            try:
                file_path = self.test_files[file_key]
                file_size = os.path.getsize(file_path)
                self.log_info(f"  文件路径: {file_path}")
                self.log_info(f"  文件大小: {file_size} 字节")

                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    response = requests.post(
                        f"{self.base_url}/api/v2/file_upload/validate",
                        headers=self.get_headers(),
                        files=files
                    )

                if response.status_code == 200:
                    result = response.json()
                    is_valid = result['is_valid']

                    if is_valid == should_pass:
                        self.log_success(f"{description} 验证结果正确: {is_valid}")
                        if not is_valid and result.get('error_message'):
                            self.log_info(f"  错误信息: {result['error_message']}")
                        success_count += 1
                    else:
                        self.log_error(f"{description} 验证结果不符合预期")
                        self.log_error(f"  期望: {should_pass}, 实际: {is_valid}")
                else:
                    self.log_error(f"{description} 验证失败: {response.text}")

            except Exception as e:
                self.log_error(f"{description} 验证异常: {str(e)}")

        return success_count == len(test_cases)

    def test_03_upload_files(self):
        """测试3: 文件上传功能"""
        self.log_step("测试3: 文件上传功能")

        # 根据是否使用本地文件调整测试用例
        if self.use_local_files:
            upload_cases = []
            if 'md_file' in self.test_files:
                upload_cases.append(("md_file", "本地MD文件", True))
            if 'pdf_file' in self.test_files:
                upload_cases.append(("pdf_file", "本地PDF文件", True))
        else:
            upload_cases = [
                ("md_file", "生成的MD文件", True),
                ("pdf_file", "生成的PDF文件", True),
            ]

        success_count = 0

        for file_key, description, should_succeed in upload_cases:
            if file_key not in self.test_files:
                continue

            self.log_info(f"上传 {description}...")

            try:
                file_path = self.test_files[file_key]
                file_size = os.path.getsize(file_path)
                self.log_info(f"  文件路径: {file_path}")
                self.log_info(f"  文件大小: {file_size} 字节")

                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    response = requests.post(
                        f"{self.base_url}/api/v2/file_upload/upload",
                        headers=self.get_headers(),
                        files=files
                    )

                # 详细输出响应信息
                self.log_info(f"  响应状态码: {response.status_code}")
                self.log_info(f"  响应内容: {response.text}")

                if response.status_code == 200:
                    result = response.json()
                    success = result['success']

                    self.log_info(f"  上传成功标志: {success}")
                    self.log_info(f"  响应消息: {result.get('message', 'N/A')}")

                    if success and should_succeed:
                        upload_id = result['upload_id']
                        self.upload_results[file_key] = upload_id
                        self.log_success(f"{description} 上传成功，ID: {upload_id}")
                        success_count += 1
                    elif not success and not should_succeed:
                        self.log_success(f"{description} 正确拒绝上传")
                        success_count += 1
                    else:
                        self.log_error(f"{description} 上传结果不符合预期")
                        self.log_error(f"  期望成功: {should_succeed}, 实际成功: {success}")
                else:
                    self.log_error(f"{description} HTTP错误: {response.status_code}")
                    self.log_error(f"  错误内容: {response.text}")

            except Exception as e:
                self.log_error(f"{description} 上传异常: {str(e)}")

        return success_count == len(upload_cases)

    def test_04_upload_history(self):
        """测试4: 上传历史管理"""
        self.log_step("测试4: 上传历史管理")

        try:
            # 获取上传历史列表
            response = requests.get(
                f"{self.base_url}/api/v2/file_upload/uploads?page=1&page_size=10",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                self.log_success("上传历史获取成功")
                self.log_info(f"  总数: {result['total']}")
                self.log_info(f"  当前页文件数: {len(result['files'])}")

                if result['files']:
                    latest_file = result['files'][0]
                    self.log_info(f"  最新文件: {latest_file['original_filename']}")
                    return latest_file['id']
                return None
            else:
                self.log_error(f"上传历史获取失败: {response.text}")
                return None

        except Exception as e:
            self.log_error(f"上传历史获取异常: {str(e)}")
            return None

    def test_05_upload_detail(self, upload_id):
        """测试5: 获取上传详情"""
        if not upload_id:
            return False

        self.log_step("测试5: 获取上传详情")

        try:
            response = requests.get(
                f"{self.base_url}/api/v2/file_upload/uploads/{upload_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                self.log_success("上传详情获取成功")
                self.log_info(f"  文件名: {result['original_filename']}")
                self.log_info(f"  状态: {result['status']}")
                self.log_info(f"  大小: {result['file_size']} 字节")
                return True
            else:
                self.log_error(f"上传详情获取失败: {response.text}")
                return False

        except Exception as e:
            self.log_error(f"上传详情获取异常: {str(e)}")
            return False

    def test_06_create_document(self):
        """测试6: 从上传文件创建文档"""
        # 优先使用MD文件创建文档
        upload_id = self.upload_results.get('md_file')
        if not upload_id:
            self.log_info("跳过文档创建测试（没有有效的MD上传）")
            return False

        self.log_step("测试6: 从上传文件创建文档")

        try:
            response = requests.post(
                f"{self.base_url}/api/v2/file_upload/create-document",
                headers=self.get_headers(),
                json={
                    "upload_id": upload_id,
                    "title": "从本地文件创建的测试文档",
                    "summary": "这是通过本地文件上传模块创建的文档"
                }
            )

            if response.status_code == 200:
                result = response.json()
                self.log_success("文档创建成功")
                self.log_info(f"  文档ID: {result['document_id']}")
                self.log_info(f"  消息: {result['message']}")
                return result['document_id']
            else:
                self.log_error(f"文档创建失败: {response.text}")
                return None

        except Exception as e:
            self.log_error(f"文档创建异常: {str(e)}")
            return None

    def test_07_get_stats(self):
        """测试7: 获取统计信息"""
        self.log_step("测试7: 获取统计信息")

        try:
            response = requests.get(
                f"{self.base_url}/api/v2/file_upload/stats",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                self.log_success("统计信息获取成功")
                self.log_info(f"  总上传数: {result['total_uploads']}")
                self.log_info(f"  总大小: {result['total_size_mb']} MB")
                self.log_info(f"  状态分布: {result['status_distribution']}")
                return True
            else:
                self.log_error(f"统计信息获取失败: {response.text}")
                return False

        except Exception as e:
            self.log_error(f"统计信息获取异常: {str(e)}")
            return False

    def cleanup(self):
        """清理测试文件"""
        self.log_step("清理测试环境")

        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                self.log_success("临时文件清理完成")
            except Exception as e:
                self.log_error(f"清理失败: {str(e)}")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始文件上传模块测试 - 本地文件版本")
        print("=" * 60)

        test_results = []

        try:
            # 设置环境
            self.setup_test_environment()

            # 执行测试
            test_results.append(("获取配置", self.test_01_get_config()))
            test_results.append(("文件验证", self.test_02_validate_files()))
            test_results.append(("文件上传", self.test_03_upload_files()))

            upload_id = self.test_04_upload_history()
            test_results.append(("上传历史", upload_id is not None))
            test_results.append(("上传详情", self.test_05_upload_detail(upload_id)))

            doc_id = self.test_06_create_document()
            test_results.append(("创建文档", doc_id is not None))
            test_results.append(("统计信息", self.test_07_get_stats()))

            # 显示测试结果
            self.log_step("测试结果汇总")
            passed = sum(1 for _, result in test_results if result)
            total = len(test_results)

            for test_name, result in test_results:
                status = "✅ 通过" if result else "❌ 失败"
                print(f"  {test_name}: {status}")

            print(f"\n📊 测试统计: {passed}/{total} 通过")

            if passed == total:
                self.log_success("🎉 所有测试通过！")
            else:
                self.log_error(f"⚠️  有 {total - passed} 个测试失败")

        except Exception as e:
            self.log_error(f"测试过程中发生严重错误: {str(e)}")
        finally:
            self.cleanup()
if __name__ == "__main__":
    print("📁 文件上传模块测试脚本")
    print("=" * 40)
    print("使用说明：")
    print("1. 请先修改脚本顶部的 LOCAL_FILES 配置")
    print("2. 将路径改为你本地的 MD 和 PDF 文件路径")
    print("3. 运行脚本时会询问是否使用本地文件")
    print("=" * 40)

tester = FileUploadTester()
tester.run_all_tests()