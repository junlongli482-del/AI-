<template>
  <div class="document-grid">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="skeleton-grid">
        <div v-for="i in skeletonCount" :key="i" class="skeleton-card">
          <el-skeleton animated>
            <template #template>
              <div class="skeleton-header">
                <el-skeleton-item variant="text" style="width: 80px; height: 20px;" />
                <el-skeleton-item variant="text" style="width: 60px; height: 20px;" />
              </div>
              <el-skeleton-item variant="h3" style="width: 80%; margin: 12px 0;" />
              <el-skeleton-item variant="text" style="width: 100%;" />
              <el-skeleton-item variant="text" style="width: 90%;" />
              <el-skeleton-item variant="text" style="width: 70%;" />
              <div class="skeleton-footer">
                <el-skeleton-item variant="text" style="width: 60px; height: 16px;" />
                <el-skeleton-item variant="text" style="width: 80px; height: 16px;" />
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <EmptyState
      v-else-if="documents.length === 0"
      :type="emptyType"
      :keyword="searchKeyword"
      @retry="$emit('retry')"
      @clear-search="$emit('clear-search')"
    />

    <!-- 文档列表 -->
    <div v-else class="documents-container">
      <!-- 结果统计 -->
      <div v-if="showResultInfo" class="result-info">
        <span class="result-text">
          {{ resultText }}
        </span>
        <div class="result-actions">
          <el-button
            v-if="searchKeyword"
            text
            @click="$emit('clear-search')"
          >
            清空搜索
          </el-button>
        </div>
      </div>

      <!-- 文档网格 -->
      <div class="grid-container">
        <DocumentCard
          v-for="document in documents"
          :key="document.id"
          :document="document"
          @click="$emit('document-click', document.id)"
        />
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more-container">
        <el-button
          v-if="!loadingMore"
          @click="$emit('load-more')"
          size="large"
          class="load-more-btn"
        >
          加载更多文档
        </el-button>
        <div v-else class="loading-more">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
      </div>

      <!-- 到底提示 -->
      <div v-else-if="documents.length > 0" class="end-tip">
        <span>已显示全部 {{ total }} 个文档</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import DocumentCard from './DocumentCard.vue'
import EmptyState from './EmptyState.vue'

// Props
const props = defineProps({
  documents: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingMore: {
    type: Boolean,
    default: false
  },
  total: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  searchKeyword: {
    type: String,
    default: ''
  },
  activeTab: {
    type: String,
    default: 'hot'
  },
  isSearchMode: {
    type: Boolean,
    default: false
  }
})

// Emits
defineEmits(['document-click', 'load-more', 'retry', 'clear-search'])

// 计算属性
const skeletonCount = computed(() => {
  // 根据屏幕大小调整骨架屏数量
  if (window.innerWidth < 768) return 6
  if (window.innerWidth < 1200) return 8
  return 12
})

const hasMore = computed(() => {
  return props.total > props.documents.length
})

const emptyType = computed(() => {
  if (props.isSearchMode) return 'search'
  return 'normal'
})

const showResultInfo = computed(() => {
  return props.documents.length > 0 && (props.isSearchMode || props.total > 0)
})

const resultText = computed(() => {
  if (props.isSearchMode) {
    return `搜索"${props.searchKeyword}"找到 ${props.total} 个结果`
  }

  const tabTexts = {
    hot: '热门文档',
    latest: '最新文档',
    all: '全部文档'
  }

  return `${tabTexts[props.activeTab] || '文档'} (${props.total})`
})
</script>

<style scoped>
.document-grid {
  margin-bottom: 32px;
}

/* 加载状态 */
.loading-container {
  padding: 20px 0;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.skeleton-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e1e4e8;
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f6f8fa;
}

/* 文档容器 */
.documents-container {
  min-height: 400px;
}

/* 结果信息 */
.result-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
}

.result-text {
  color: #24292f;
  font-weight: 500;
}

.result-actions {
  display: flex;
  gap: 12px;
}

/* 网格容器 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

/* 加载更多 */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

.load-more-btn {
  padding: 12px 32px;
  font-size: 16px;
  border-radius: 8px;
}

.loading-more {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #656d76;
  font-size: 14px;
}

.loading-more .el-icon {
  font-size: 16px;
}

/* 到底提示 */
.end-tip {
  text-align: center;
  padding: 24px 0;
  color: #656d76;
  font-size: 14px;
  border-top: 1px solid #f6f8fa;
}

/* 响应式 */
@media (max-width: 768px) {
  .skeleton-grid,
  .grid-container {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .result-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
  }

  .result-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .load-more-btn {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .skeleton-card {
    padding: 16px;
  }
}
</style>
