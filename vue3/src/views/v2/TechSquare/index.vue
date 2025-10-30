<template>
  <div class="tech-square">
    <!-- 全局导航 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">技术广场</h1>
          <p class="page-subtitle">发现优质技术内容，分享开发经验</p>
        </div>
        <div class="header-stats">
          <div class="stat-card">
            <span class="stat-number">{{ formatCount(stats.total_documents) }}</span>
            <span class="stat-label">文档</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ formatCount(stats.total_views) }}</span>
            <span class="stat-label">阅读</span>
          </div>
          <div class="stat-card">
            <span class="stat-number">{{ stats.today_published }}</span>
            <span class="stat-label">今日发布</span>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-section">
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文档..."
            size="large"
            @keyup.enter="handleSearch"
            clearable
          >
            <template #prefix>
              <span class="search-icon">🔍</span>
            </template>
            <template #append>
              <el-button @click="handleSearch" type="primary">搜索</el-button>
            </template>
          </el-input>
        </div>

        <!-- 标签栏 -->
        <div v-if="pageMode === 'normal'" class="tabs-section">
          <div class="tab-buttons">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              :class="['tab-btn', { active: activeTab === tab.key }]"
              @click="switchTab(tab.key)"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-text">{{ tab.label }}</span>
            </button>
          </div>
        </div>

        <!-- 搜索结果提示 -->
        <div v-else class="search-result-info">
          <span class="result-text">找到 {{ searchTotal }} 个相关文档</span>
          <el-button @click="clearSearch" text type="primary">清空搜索</el-button>
        </div>
      </div>

      <!-- 文档列表 -->
      <div class="documents-section">
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="6" animated />
        </div>

        <div v-else-if="documents.length === 0" class="empty-state">
          <div class="empty-icon">📄</div>
          <p class="empty-text">{{ pageMode === 'search' ? '没有找到相关文档' : '暂无文档' }}</p>
        </div>

        <div v-else class="documents-grid">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="document-card"
            @click="viewDocument(doc.id)"
          >
            <!-- 卡片头部 -->
            <div class="card-header">
              <div class="file-type">
                <span class="type-icon">{{ getFileTypeIcon(doc.file_type) }}</span>
                <span class="type-text">{{ getFileTypeText(doc.file_type) }}</span>
              </div>
              <div v-if="doc.is_featured" class="featured-tag">⭐</div>
            </div>

            <!-- 文档内容 -->
            <div class="card-content">
              <h3 class="doc-title">{{ doc.title }}</h3>
              <p v-if="doc.summary" class="doc-summary">{{ doc.summary }}</p>
            </div>

            <!-- 卡片底部 -->
            <div class="card-footer">
              <div class="author-info">
                <span class="author-avatar">{{ getAuthorAvatar(doc) }}</span>
                <span class="author-name">{{ getAuthorDisplayName(doc) }}</span>
              </div>

              <div class="doc-stats">
                <span class="stat-item">
                  <span class="stat-icon">👀</span>
                  <span class="stat-text">{{ formatViewCount(doc.view_count) }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-icon">❤️</span>
                  <span class="stat-text">{{ formatInteractionCount(doc.like_count || 0) }}</span>
                </span>
              </div>
            </div>

            <!-- 时间信息 -->
            <div class="card-time">
              {{ formatTime(doc.publish_time) }}
            </div>
          </div>
        </div>

        <!-- 加载更多 -->
        <div v-if="hasMore && !loading" class="load-more">
          <el-button
            @click="loadMore"
            :loading="loadingMore"
            size="large"
            class="load-more-btn"
          >
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// ... 脚本部分保持不变
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import {
  getStats,
  getDocuments,
  searchDocuments,
  formatTime,
  formatViewCount,
  getFileTypeIcon,
  getFileTypeText
} from '@/api/v2/tech_square'
import {
  formatInteractionCount,
  getBatchInteractionStatus
} from '@/api/v2/interaction'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 标签配置
const tabs = [
  { key: 'hot', label: '热门', icon: '🔥' },
  { key: 'latest', label: '最新', icon: '⚡' },
  { key: 'all', label: '全部', icon: '📚' }
]

// 响应式数据
const loading = ref(false)
const loadingMore = ref(false)
const pageMode = ref('normal')
const activeTab = ref('hot')
const searchKeyword = ref('')
const searchTotal = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const hasMore = computed(() => total.value > documents.value.length)

const stats = reactive({
  total_documents: 0,
  total_views: 0,
  today_published: 0,
  featured_count: 0
})

const documents = ref([])

// 生命周期
onMounted(() => {
  loadStats()
  loadDocuments('hot')
})

// 监听登录状态变化
watch(() => userStore.token, (newToken) => {
  if (newToken && documents.value.length > 0) {
    loadInteractionStates()
  }
})

// 方法
const formatCount = (count) => {
  if (count >= 10000) return `${(count / 10000).toFixed(1)}w`
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k`
  return count.toString()
}

const getAuthorAvatar = (doc) => {
  const name = getAuthorDisplayName(doc)
  return name.charAt(0).toUpperCase()
}

const getAuthorDisplayName = (doc) => {
  if (!doc) return '未知'
  return doc.nickname || doc.username || `用户${doc.user_id}`
}

const loadStats = async () => {
  try {
    const response = await getStats()
    Object.assign(stats, response)
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadInteractionStates = async () => {
  if (!userStore.token || documents.value.length === 0) return

  try {
    const documentIds = documents.value.map(doc => doc.id)
    const statusMap = await getBatchInteractionStatus(documentIds)

    documents.value.forEach(doc => {
      const status = statusMap[doc.id]
      if (status) {
        doc.like_count = status.like_count
        doc.favorite_count = status.favorite_count
        doc.is_liked = status.is_liked
        doc.is_favorited = status.is_favorited
      }
    })
  } catch (error) {
    console.warn('加载互动状态失败:', error)
  }
}

const loadDocuments = async (sortType = 'latest', page = 1, append = false) => {
  if (!append) loading.value = true
  else loadingMore.value = true

  try {
    const params = {
      page,
      size: pageSize.value,
      sort_by: sortType === 'hot' ? 'popular' : sortType === 'all' ? 'latest' : sortType
    }

    const response = await getDocuments(params)

    if (append) {
      documents.value.push(...(response.documents || []))
    } else {
      documents.value = response.documents || []
    }

    total.value = response.total || 0
    currentPage.value = response.page || 1

    if (userStore.token) {
      await loadInteractionStates()
    }
  } catch (error) {
    console.error('加载文档失败:', error)
    ElMessage.error('加载文档失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const performSearch = async (keyword, page = 1, append = false) => {
  if (!keyword.trim()) return

  if (!append) loading.value = true
  else loadingMore.value = true

  try {
    const params = {
      keyword: keyword.trim(),
      page,
      size: pageSize.value
    }

    const response = await searchDocuments(params)

    if (append) {
      documents.value.push(...(response.documents || []))
    } else {
      documents.value = response.documents || []
    }

    total.value = response.total || 0
    searchTotal.value = response.total || 0
    currentPage.value = response.page || 1

    if (userStore.token) {
      await loadInteractionStates()
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const switchTab = (tab) => {
  activeTab.value = tab
  pageMode.value = 'normal'
  searchKeyword.value = ''
  currentPage.value = 1
  loadDocuments(tab)
}

const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    clearSearch()
    return
  }

  pageMode.value = 'search'
  currentPage.value = 1
  performSearch(keyword)
}

const clearSearch = () => {
  pageMode.value = 'normal'
  searchKeyword.value = ''
  activeTab.value = 'hot'
  currentPage.value = 1
  loadDocuments('hot')
}

const loadMore = () => {
  const nextPage = currentPage.value + 1

  if (pageMode.value === 'search') {
    performSearch(searchKeyword.value, nextPage, true)
  } else {
    loadDocuments(activeTab.value, nextPage, true)
  }
}

const viewDocument = (documentId) => {
  router.push(`/tech-square/document/${documentId}`)
}
</script>

<style scoped>
.tech-square {
  min-height: 100vh;
  background: linear-gradient(135deg,
  rgba(255, 154, 158, 0.1) 0%,
  rgba(250, 208, 196, 0.1) 25%,
  rgba(168, 237, 234, 0.1) 50%,
  rgba(254, 214, 227, 0.1) 75%,
  rgba(255, 234, 167, 0.1) 100%
  );
  backdrop-filter: blur(20px);
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-content h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  font-size: 16px;
  color: #86868b;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-card {
  text-align: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #86868b;
  font-weight: 500;
}

/* 搜索区域 */
.search-section {
  margin-bottom: 32px;
}

.search-bar {
  margin-bottom: 24px;
}

.search-icon {
  font-size: 16px;
  color: #86868b;
}

.tabs-section {
  display: flex;
  justify-content: center;
}

.tab-buttons {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  background: transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  color: #86868b;
}

.tab-btn.active {
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.tab-btn:hover:not(.active) {
  background: rgba(0, 122, 255, 0.08);
  color: #1d1d1f;
}

.search-result-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.result-text {
  font-size: 14px;
  color: #86868b;
}

/* 文档列表 */
.loading-state,
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #86868b;
  margin: 0;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

/* 文档卡片 */
.document-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.document-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  border-color: rgba(0, 122, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.file-type {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 122, 255, 0.1);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: #007AFF;
}

.featured-tag {
  font-size: 16px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.card-content {
  flex: 1;
  margin-bottom: 20px;
}

.doc-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.doc-summary {
  font-size: 14px;
  color: #86868b;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  margin-bottom: 12px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.author-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.doc-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #86868b;
}

.stat-icon {
  font-size: 14px;
}

.card-time {
  font-size: 12px;
  color: #86868b;
  text-align: right;
}

/* 加载更多 */
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.load-more-btn {
  padding: 16px 40px;
  border-radius: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.load-more-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.4);
}

/* 响应式 */
@media (max-width: 1024px) {
  .page-header {
    flex-direction: column;
    gap: 24px;
    text-align: center;
  }

  .header-stats {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px 16px;
  }

  .page-header {
    padding: 24px 20px;
  }

  .header-content h1 {
    font-size: 28px;
  }

  .header-stats {
    gap: 16px;
  }

  .stat-card {
    padding: 12px 16px;
  }

  .documents-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .document-card {
    padding: 20px;
  }

  .tab-buttons {
    width: 100%;
    justify-content: center;
  }

  .search-result-info {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

:deep(.el-button) {
  border-radius: 12px;
}
</style>
