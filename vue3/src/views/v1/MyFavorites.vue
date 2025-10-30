<template>
  <div class="favorites-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/home')">用户系统</h1>
        <div class="user-menu">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
              <span class="arrow">▼</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="user-center">👤 个人中心</el-dropdown-item>
                <el-dropdown-item command="home">🏠 返回主页</el-dropdown-item>
                <el-dropdown-item command="logout" divided>🚪 退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="favorites-card">
        <!-- 页面标题和返回按钮 -->
        <div class="page-header">
          <div class="header-left">
            <el-button
              text
              @click="$router.push('/user-center')"
              class="back-button"
            >
              ← 返回个人中心
            </el-button>
            <h2 class="page-title">我的收藏</h2>
          </div>
          <div class="header-stats">
            <span class="stats-text">共 {{ totalFavorites }} 个收藏</span>
          </div>
        </div>

        <!-- 收藏列表 -->
        <div class="favorites-content">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-state">
            <el-skeleton :rows="3" animated />
          </div>

          <!-- 空状态 -->
          <div v-else-if="favoritesList.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <h3 class="empty-title">暂无收藏</h3>
            <p class="empty-description">去技术广场发现优质内容吧！</p>
            <el-button
              type="primary"
              @click="$router.push('/tech-square')"
              class="empty-action"
            >
              去技术广场
            </el-button>
          </div>

          <!-- 收藏列表 -->
          <div v-else class="favorites-list">
            <div
              v-for="item in favoritesList"
              :key="item.id"
              class="favorite-item"
            >
              <div class="item-content" @click="viewDocument(item.document_id)">
                <div class="item-header">
                  <h3 class="item-title">{{ item.document_title }}</h3>
                  <div class="item-type">
                    <span class="type-badge" :class="item.file_type">
                      {{ item.file_type.toUpperCase() }}
                    </span>
                  </div>
                </div>

                <p class="item-summary">{{ item.document_summary || '暂无摘要' }}</p>

                <div class="item-footer">
                  <span class="favorite-time">
                    收藏于 {{ formatDate(item.created_at) }}
                  </span>
                </div>
              </div>

              <div class="item-actions">
                <el-button
                  text
                  type="primary"
                  @click="viewDocument(item.document_id)"
                  class="action-btn"
                >
                  查看
                </el-button>
                <el-button
                  text
                  type="danger"
                  @click="removeFavorite(item)"
                  :loading="removingIds.includes(item.document_id)"
                  class="action-btn"
                >
                  取消收藏
                </el-button>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="totalPages > 1" class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="totalFavorites"
              layout="prev, pager, next"
              @current-change="handlePageChange"
              class="favorites-pagination"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getMyFavorites, toggleFavorite } from '@/api/v2/interaction'

const router = useRouter()
const userStore = useUserStore()

// 数据状态
const loading = ref(false)
const favoritesList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalFavorites = ref(0)
const removingIds = ref([])

// 计算属性
const totalPages = computed(() => Math.ceil(totalFavorites.value / pageSize.value))

onMounted(() => {
  loadFavorites()
})

// 加载收藏列表
const loadFavorites = async () => {
  loading.value = true
  try {
    const response = await getMyFavorites({
      page: currentPage.value,
      size: pageSize.value
    })

    favoritesList.value = response.items
    totalFavorites.value = response.total
  } catch (error) {
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

// 查看文档
const viewDocument = (documentId) => {
  router.push(`/tech-square/document/${documentId}`)
}

// 取消收藏
const removeFavorite = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消收藏《${item.document_title}》吗？`,
      '取消收藏',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    removingIds.value.push(item.document_id)

    try {
      await toggleFavorite(item.document_id)
      ElMessage.success('取消收藏成功')

      // 从列表中移除
      favoritesList.value = favoritesList.value.filter(
        fav => fav.document_id !== item.document_id
      )
      totalFavorites.value--

      // 如果当前页没有数据且不是第一页，跳转到上一页
      if (favoritesList.value.length === 0 && currentPage.value > 1) {
        currentPage.value--
        loadFavorites()
      }
    } catch (error) {
      ElMessage.error('取消收藏失败')
    } finally {
      removingIds.value = removingIds.value.filter(id => id !== item.document_id)
    }
  } catch {
    // 用户取消
  }
}

// 分页切换
const handlePageChange = (page) => {
  currentPage.value = page
  loadFavorites()
}

// 头部菜单操作
const handleCommand = async (command) => {
  if (command === 'user-center') {
    router.push('/user-center')
  } else if (command === 'home') {
    router.push('/home')
  } else if (command === 'logout') {
    await handleLogout()
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes < 1 ? '刚刚' : `${minutes}分钟前`
  }

  // 小于24小时
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }

  // 小于7天
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }

  // 超过7天显示具体日期
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style scoped>
.favorites-container {
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,245,0.95) 100%);
  backdrop-filter: blur(20px);
}

.header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.5px;
  cursor: pointer;
  transition: color 0.2s;
}

.logo:hover {
  color: #007AFF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(0, 0, 0, 0.04);
}

.username {
  font-size: 15px;
  font-weight: 500;
  color: #1d1d1f;
}

.arrow {
  font-size: 12px;
  color: #86868b;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 48px 24px;
}

.favorites-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  padding: 48px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  color: #86868b;
  font-size: 14px;
  padding: 8px 0;
}

.back-button:hover {
  color: #007AFF;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.5px;
}

.header-stats {
  display: flex;
  align-items: center;
}

.stats-text {
  font-size: 14px;
  color: #86868b;
  background: rgba(0, 0, 0, 0.04);
  padding: 6px 12px;
  border-radius: 8px;
}

.favorites-content {
  min-height: 400px;
}

.loading-state {
  padding: 40px 0;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px 0;
}

.empty-description {
  font-size: 16px;
  color: #86868b;
  margin: 0 0 32px 0;
}

.empty-action {
  min-width: 140px;
  height: 44px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.favorite-item {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: all 0.3s ease;
}

.favorite-item:hover {
  background: rgba(255, 255, 255, 0.8);
  border-color: rgba(0, 122, 255, 0.2);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.item-content {
  flex: 1;
  cursor: pointer;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  line-height: 1.4;
  flex: 1;
  margin-right: 16px;
}

.item-type {
  flex-shrink: 0;
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.type-badge.md {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
}

.type-badge.pdf {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: white;
}

.item-summary {
  font-size: 14px;
  color: #86868b;
  line-height: 1.5;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.favorite-time {
  font-size: 13px;
  color: #86868b;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 24px;
}

.action-btn {
  min-width: 80px;
  height: 32px;
  font-size: 14px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.favorites-pagination {
  --el-pagination-button-color: #86868b;
  --el-pagination-hover-color: #007AFF;
}

:deep(.el-dropdown-menu__item) {
  padding: 12px 20px;
}

:deep(.el-skeleton__item) {
  background: linear-gradient(90deg, rgba(0, 0, 0, 0.04) 25%, rgba(0, 0, 0, 0.02) 50%, rgba(0, 0, 0, 0.04) 75%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 24px 16px;
  }

  .favorites-card {
    padding: 24px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .favorite-item {
    flex-direction: column;
    gap: 16px;
  }

  .item-actions {
    flex-direction: row;
    margin-left: 0;
    align-self: stretch;
  }

  .action-btn {
    flex: 1;
  }
}
</style>
