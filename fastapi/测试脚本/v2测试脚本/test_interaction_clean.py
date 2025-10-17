import requests
import json
import time
import random
import string
from datetime import datetime


class InteractionModuleTest:
    def __init__(self):
        self.base_url = "http://localhost:8100"
        self.access_token = None
        self.test_document_id = None
        self.test_comment_id = None

    def login(self):
        """用户登录获取token"""
        login_data = {
            "username_or_email": "abc",
            "password": "ljl18420"
        }

        response = requests.post(f"{self.base_url}/api/v1/user_auth/login", json=login_data)

        if response.status_code == 200:
            result = response.json()
            # 🔧 修复：直接从根级别获取access_token
            self.access_token = result["access_token"]
            print("✅ 用户登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.text}")
            return False

    def get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def test_module_connectivity(self):
        """测试模块连通性"""
        try:
            response = requests.get(f"{self.base_url}/api/v2/interaction/test")

            if response.status_code == 200:
                result = response.json()
                print("✅ 模块连通性正常")
                return True
            else:
                print(f"❌ 模块连通性测试失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 模块连通性测试异常: {str(e)}")
            return False

    def create_test_document(self):
        """创建测试文档"""
        try:
            # 生成唯一标题
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
            title = f"互动测试文档_{timestamp}_{random_suffix}"

            doc_data = {
                "title": title,
                "content": "这是一个用于测试互动功能的文档内容。包含点赞、收藏、评论等功能测试。",
                "file_type": "md",
                "summary": "互动功能测试文档"
            }

            response = requests.post(
                f"{self.base_url}/api/v2/document_manager/documents",
                json=doc_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                result = response.json()
                # 🔧 修复：直接从根级别获取id
                self.test_document_id = result["id"]
                print(f"✅ 创建测试文档成功 (ID: {self.test_document_id}, 标题: {title})")

                # 发布文档以便测试
                self.publish_test_document()
                return True
            else:
                print(f"❌ 创建测试文档失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 创建测试文档异常: {str(e)}")
            return False

    def publish_test_document(self):
        """发布测试文档"""
        try:
            if not self.test_document_id:
                print("❌ 文档ID无效，跳过发布")
                return False

            publish_data = {
                "publish_reason": "互动功能测试文档"
            }

            response = requests.post(
                f"{self.base_url}/api/v2/document_publish/submit",
                json=publish_data,
                headers=self.get_headers(),
                params={"document_id": self.test_document_id}
            )

            if response.status_code == 200:
                print("✅ 文档发布申请成功")

                # 等待发布完成
                for i in range(15):
                    time.sleep(1)
                    status_response = requests.get(
                        f"{self.base_url}/api/v2/document_publish/status/{self.test_document_id}",
                        headers=self.get_headers()
                    )

                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        # 🔧 修复：适配不同的响应格式
                        if "data" in status_result:
                            publish_status = status_result["data"].get('publish_status', 'unknown')
                        else:
                            publish_status = status_result.get('publish_status', 'unknown')

                        print(f"⏳ 发布状态检查 {i + 1}/15: {publish_status}")

                        if publish_status == "published":
                            print("✅ 文档发布成功")
                            return True
                        elif publish_status == "review_failed":
                            print("❌ 文档审核失败")
                            return False

                print("⚠️ 发布超时，但继续测试")
                return True
            else:
                print(f"❌ 文档发布失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 发布文档异常: {str(e)}")
            return False

    def test_like_functionality(self):
        """测试点赞功能"""
        try:
            # 🔧 添加安全检查
            if not self.test_document_id:
                print("❌ 测试文档ID无效，跳过点赞功能测试")
                return False
            # 1. 获取初始点赞状态
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/like-status",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                initial_status = response.json()
                print(
                    f"✅ 获取初始点赞状态成功 (已点赞: {initial_status['is_liked']}, 点赞数: {initial_status['like_count']})")
            else:
                print(f"❌ 获取点赞状态失败: {response.text}")
                return False

            # 2. 点赞操作
            response = requests.post(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/like",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                like_result = response.json()
                print(f"✅ 点赞操作成功 (状态: {like_result['message']}, 点赞数: {like_result['like_count']})")
            else:
                print(f"❌ 点赞操作失败: {response.text}")
                return False

            # 3. 再次点赞（取消点赞）
            response = requests.post(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/like",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                unlike_result = response.json()
                print(f"✅ 取消点赞成功 (状态: {unlike_result['message']}, 点赞数: {unlike_result['like_count']})")
            else:
                print(f"❌ 取消点赞失败: {response.text}")
                return False

            return True
        except Exception as e:
            print(f"❌ 点赞功能测试异常: {str(e)}")
            return False

    def test_favorite_functionality(self):
        """测试收藏功能"""
        try:
            # 🔧 添加安全检查
            if not self.test_document_id:
                print("❌ 测试文档ID无效，跳过点赞功能测试")
                return False
            # 1. 获取初始收藏状态
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/favorite-status",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                initial_status = response.json()
                print(
                    f"✅ 获取初始收藏状态成功 (已收藏: {initial_status['is_favorited']}, 收藏数: {initial_status['favorite_count']})")
            else:
                print(f"❌ 获取收藏状态失败: {response.text}")
                return False

            # 2. 收藏操作
            response = requests.post(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/favorite",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                favorite_result = response.json()
                print(
                    f"✅ 收藏操作成功 (状态: {favorite_result['message']}, 收藏数: {favorite_result['favorite_count']})")
            else:
                print(f"❌ 收藏操作失败: {response.text}")
                return False

            # 3. 获取我的收藏列表
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/my-favorites?page=1&size=10",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                favorites_result = response.json()
                print(f"✅ 获取收藏列表成功 (总数: {favorites_result['total']})")
            else:
                print(f"❌ 获取收藏列表失败: {response.text}")
                return False

            return True
        except Exception as e:
            print(f"❌ 收藏功能测试异常: {str(e)}")
            return False

    def test_comment_functionality(self):
        """测试评论功能"""
        try:
            # 🔧 添加安全检查
            if not self.test_document_id:
                print("❌ 测试文档ID无效，跳过点赞功能测试")
                return False
            # 1. 创建评论
            comment_data = {
                "content": "这是一个测试评论，用于验证评论功能是否正常工作。"
            }

            response = requests.post(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/comments",
                json=comment_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                comment_result = response.json()
                self.test_comment_id = comment_result["comment"]["id"]
                print(f"✅ 创建评论成功 (ID: {self.test_comment_id})")
            else:
                print(f"❌ 创建评论失败: {response.text}")
                return False

            # 2. 创建回复
            reply_data = {
                "content": "这是对评论的回复，测试二层评论结构。",
                "parent_id": self.test_comment_id
            }

            response = requests.post(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/comments",
                json=reply_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                reply_result = response.json()
                print(f"✅ 创建回复成功 (ID: {reply_result['comment']['id']})")
            else:
                print(f"❌ 创建回复失败: {response.text}")
                return False

            # 3. 获取评论列表
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/comments?page=1&size=10"
            )

            if response.status_code == 200:
                comments_result = response.json()
                print(f"✅ 获取评论列表成功 (总数: {comments_result['total']})")

                # 验证回复结构
                if comments_result["items"]:
                    first_comment = comments_result["items"][0]
                    print(f"   - 评论回复数: {first_comment['reply_count']}")
            else:
                print(f"❌ 获取评论列表失败: {response.text}")
                return False

            # 4. 更新评论
            update_data = {
                "content": "这是更新后的评论内容，测试评论编辑功能。"
            }

            response = requests.put(
                f"{self.base_url}/api/v2/interaction/comments/{self.test_comment_id}",
                json=update_data,
                headers=self.get_headers()
            )

            if response.status_code == 200:
                print("✅ 更新评论成功")
            else:
                print(f"❌ 更新评论失败: {response.text}")
                return False

            return True
        except Exception as e:
            print(f"❌ 评论功能测试异常: {str(e)}")
            return False

    def test_stats_functionality(self):
        """测试统计功能"""
        try:
            # 🔧 添加安全检查
            if not self.test_document_id:
                print("❌ 测试文档ID无效，跳过点赞功能测试")
                return False
            # 1. 获取文档统计
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/documents/{self.test_document_id}/stats"
            )

            if response.status_code == 200:
                doc_stats = response.json()
                print(f"✅ 获取文档统计成功")
                print(f"   - 点赞数: {doc_stats['like_count']}")
                print(f"   - 收藏数: {doc_stats['favorite_count']}")
                print(f"   - 评论数: {doc_stats['comment_count']}")
            else:
                print(f"❌ 获取文档统计失败: {response.text}")
                return False

            # 2. 获取用户统计
            response = requests.get(
                f"{self.base_url}/api/v2/interaction/my-stats",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                user_stats = response.json()
                print(f"✅ 获取用户统计成功")
                print(f"   - 给出点赞: {user_stats['total_likes_given']}")
                print(f"   - 收藏文档: {user_stats['total_favorites']}")
                print(f"   - 发表评论: {user_stats['total_comments']}")
                print(f"   - 收到点赞: {user_stats['total_likes_received']}")
                print(f"   - 收到收藏: {user_stats['total_favorites_received']}")
                print(f"   - 收到评论: {user_stats['total_comments_received']}")
            else:
                print(f"❌ 获取用户统计失败: {response.text}")
                return False

            return True
        except Exception as e:
            print(f"❌ 统计功能测试异常: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始Interaction模块测试")
        print("=" * 50)

        tests = [
            ("用户登录", self.login),
            ("模块连通性", self.test_module_connectivity),
            ("创建测试文档", self.create_test_document),
            ("点赞功能", self.test_like_functionality),
            ("收藏功能", self.test_favorite_functionality),
            ("评论功能", self.test_comment_functionality),
            ("统计功能", self.test_stats_functionality),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {str(e)}")

        print("=" * 50)
        print(f"📊 测试完成: {passed}/{total} 通过")

        if passed == total:
            print("🎉 所有测试通过! Interaction模块运行正常")
        else:
            print(f"⚠️ 有 {total - passed} 个测试失败，请检查相关功能")

        return passed == total


if __name__ == "__main__":
    tester = InteractionModuleTest()
    tester.run_all_tests()