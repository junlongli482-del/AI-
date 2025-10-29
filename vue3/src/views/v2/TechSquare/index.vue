<template>
  <div class="tech-square">
    <!-- 全局导航 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 搜索区域 -->
      <SearchSection
        v-model="searchKeyword"
        @search="handleSearch"
        @clear="clearSearch"
      />

      <!-- 统计数据卡片 -->
      <StatsCards :stats="stats" />

      <!-- 标签栏 / 筛选器 -->
      <TabsSection
        v-if="pageMode === 'normal'"
        :active-tab="activeTab"
        :stats="stats"
        :loading="loading"
        @tab-change="switchTab"
      />

      <FiltersSection
        v-else
        :search-keyword="searchKeyword"
        :total="searchTotal"
        :file-type="fileTypeFilter"
        :time-filter="timeFilter"
        :sort-by="sortBy"
        @filter-change="handleFilterChange"
        @clear-search="clearSearch"
        @reset-filters="resetFilters"
      />

      <!-- 文档列表 -->
      <div class="documents-section">
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="6" animated />
        </div>

        <div v-else-if="documents.length === 0" class="empty-container">
          <el-empty
            :description="pageMode === 'search' ? '没有找到相关文档' : '暂无文档'"
            :image-size="120"
          />
        </div>

        <div v-else class="documents-grid">
          <DocumentCard
            v-for="doc in documents"
            :key="doc.id"
            :document="doc"
            @click="viewDocument(doc.id)"
          />
        </div>

        <!-- 分页组件 -->
        <div v-if="totalPages > 1" class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next, jumper"
            @current-change="handlePageChange"
          />
        </div>

        <!-- 加载更多按钮 -->
        <div v-if="hasMore && !loading" class="load-more-container">
          <el-button
            @click="loadMore"
            :loading="loadingMore"
            size="large"
            class="load-more-btn"
          >
            {{ loadingMore ? '加载中...' : '加载更多文档' }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import SearchSection from './components/SearchSection.vue'
import StatsCards from './components/StatsCards.vue'
import TabsSection from './components/TabsSection.vue'
import FiltersSection from './components/FiltersSection.vue'
import DocumentCard from './components/DocumentCard.vue'
import {
  getStats,
  getDocuments,
  searchDocuments
} from '@/api/v2/tech_square'

const router = useRouter()

// ==================== 响应式数据 ====================
const loading = ref(false)
const loadingMore = ref(false)
const pageMode = ref('normal') // 'normal' | 'search'
const activeTab = ref('hot') // 'hot' | 'latest' | 'all'

// 搜索相关
const searchKeyword = ref('')
const searchTotal = ref(0)

// 筛选相关
const fileTypeFilter = ref('')
const timeFilter = ref('')
const sortBy = ref('relevance')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
const hasMore = computed(() => total.value > documents.value.length)

// 数据
const stats = reactive({
  total_documents: 0,
  total_views: 0,
  today_published: 0,
  featured_count: 0
})
const documents = ref([])

// ==================== 生命周期 ====================
onMounted(() => {
  loadStats()
  loadDocuments('hot') // 默认加载最热文档
})

// ==================== 方法 ====================

/**
 * 加载统计信息
 */
const loadStats = async () => {
  try {
    const response = await getStats()
    Object.assign(stats, response)
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

/**
 * 加载文档列表
 */
const loadDocuments = async (sortType = 'latest', page = 1, append = false) => {
  if (!append) {
    loading.value = true
  } else {
    loadingMore.value = true
  }

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
  } catch (error) {
    console.error('加载文档列表失败:', error)
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

/**
 * 搜索文档
 */
const performSearch = async (keyword, page = 1, append = false) => {
  if (!keyword.trim()) return

  if (!append) {
    loading.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const params = {
      keyword: keyword.trim(),
      page,
      size: pageSize.value
    }

    // 添加筛选条件
    if (fileTypeFilter.value) {
      params.file_type = fileTypeFilter.value
    }
    if (timeFilter.value) {
      params.time_filter = timeFilter.value
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
  } catch (error) {
    console.error('搜索文档失败:', error)
    ElMessage.error('搜索文档失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

/**
 * 标签切换
 */
const switchTab = (tab) => {
  activeTab.value = tab
  pageMode.value = 'normal'
  searchKeyword.value = ''
  resetFilters()
  currentPage.value = 1

  loadDocuments(tab)
}

/**
 * 执行搜索
 */
const handleSearch = (keyword) => {
  if (!keyword.trim()) {
    clearSearch()
    return
  }

  pageMode.value = 'search'
  searchKeyword.value = keyword
  currentPage.value = 1
  resetFilters()

  performSearch(keyword)
}

/**
 * 清空搜索
 */
const clearSearch = () => {
  pageMode.value = 'normal'
  searchKeyword.value = ''
  resetFilters()
  activeTab.value = 'hot'
  currentPage.value = 1

  loadDocuments('hot')
}

/**
 * 筛选条件变化
 */
const handleFilterChange = (filters) => {
  // 更新筛选值
  if (filters.fileType !== undefined) fileTypeFilter.value = filters.fileType
  if (filters.timeFilter !== undefined) timeFilter.value = filters.timeFilter
  if (filters.sortBy !== undefined) sortBy.value = filters.sortBy

  // 重新搜索
  if (pageMode.value === 'search') {
    currentPage.value = 1
    performSearch(searchKeyword.value)
  }
}

/**
 * 重置筛选器
 */
const resetFilters = () => {
  fileTypeFilter.value = ''
  timeFilter.value = ''
  sortBy.value = 'relevance'
}

/**
 * 分页变化
 */
const handlePageChange = (page) => {
  currentPage.value = page

  if (pageMode.value === 'search') {
    performSearch(searchKeyword.value, page)
  } else {
    loadDocuments(activeTab.value, page)
  }
}

/**
 * 加载更多
 */
const loadMore = () => {
  const nextPage = currentPage.value + 1

  if (pageMode.value === 'search') {
    performSearch(searchKeyword.value, nextPage, true)
  } else {
    loadDocuments(activeTab.value, nextPage, true)
  }
}

/**
 * 查看文档详情
 */
const viewDocument = (documentId) => {
  router.push(`/tech-square/document/${documentId}`)
}
</script>

<style scoped>
.tech-square {
  min-height: 100vh;
  background: #fafbfc;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* 文档列表 */
.documents-section {
  margin-bottom: 32px;
}

.loading-container,
.empty-container {
  padding: 40px 0;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* 加载更多 */
.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.load-more-btn {
  padding: 12px 32px;
  font-size: 16px;
  border-radius: 8px;
  min-width: 200px;
}

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .documents-grid {
    grid-template-columns: 1fr;
  }

  .load-more-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>
