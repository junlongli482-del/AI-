<template>
  <div class="filters-section">
    <div class="filters-container">
      <!-- 搜索信息 -->
      <div class="search-info">
        <div class="search-keyword">
          <el-icon><Search /></el-icon>
          <span>搜索"{{ searchKeyword }}"</span>
        </div>
        <div class="search-result">
          找到 <strong>{{ total }}</strong> 个结果
        </div>
      </div>

      <!-- 筛选器 -->
      <div class="filters-row">
        <div class="filters-group">
          <!-- 文件类型筛选 -->
          <div class="filter-item">
            <label class="filter-label">文件类型</label>
            <el-select
              :model-value="fileType"
              @change="handleFilterChange('fileType', $event)"
              placeholder="全部类型"
              clearable
            >
              <el-option label="全部类型" value="" />
              <el-option label="📝 MD文档" value="md" />
              <el-option label="📄 PDF文档" value="pdf" />
            </el-select>
          </div>

          <!-- 时间筛选 -->
          <div class="filter-item">
            <label class="filter-label">发布时间</label>
            <el-select
              :model-value="timeFilter"
              @change="handleFilterChange('timeFilter', $event)"
              placeholder="全部时间"
              clearable
            >
              <el-option label="全部时间" value="" />
              <el-option label="今日" value="today" />
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
            </el-select>
          </div>

          <!-- 排序方式 -->
          <div class="filter-item">
            <label class="filter-label">排序方式</label>
            <el-select
              :model-value="sortBy"
              @change="handleFilterChange('sortBy', $event)"
            >
              <el-option label="相关性" value="relevance" />
              <el-option label="最新发布" value="latest" />
              <el-option label="最受欢迎" value="popular" />
            </el-select>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="filter-actions">
          <el-button @click="handleReset" :disabled="!hasActiveFilters">
            重置筛选
          </el-button>
          <el-button type="primary" @click="$emit('clear-search')">
            清空搜索
          </el-button>
        </div>
      </div>

      <!-- 活跃筛选标签 -->
      <div v-if="activeFilters.length > 0" class="active-filters">
        <span class="filters-label">当前筛选：</span>
        <el-tag
          v-for="filter in activeFilters"
          :key="filter.key"
          @close="handleRemoveFilter(filter.key)"
          closable
          class="filter-tag"
        >
          {{ filter.label }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  searchKeyword: {
    type: String,
    required: true
  },
  total: {
    type: Number,
    default: 0
  },
  fileType: {
    type: String,
    default: ''
  },
  timeFilter: {
    type: String,
    default: ''
  },
  sortBy: {
    type: String,
    default: 'relevance'
  }
})

// Emits
const emit = defineEmits(['filter-change', 'clear-search', 'reset-filters'])

// 计算属性
const hasActiveFilters = computed(() => {
  return props.fileType || props.timeFilter || props.sortBy !== 'relevance'
})

const activeFilters = computed(() => {
  const filters = []

  if (props.fileType) {
    const typeLabels = {
      md: 'MD文档',
      pdf: 'PDF文档'
    }
    filters.push({
      key: 'fileType',
      label: typeLabels[props.fileType]
    })
  }

  if (props.timeFilter) {
    const timeLabels = {
      today: '今日',
      week: '本周',
      month: '本月'
    }
    filters.push({
      key: 'timeFilter',
      label: timeLabels[props.timeFilter]
    })
  }

  if (props.sortBy && props.sortBy !== 'relevance') {
    const sortLabels = {
      latest: '最新发布',
      popular: '最受欢迎'
    }
    filters.push({
      key: 'sortBy',
      label: sortLabels[props.sortBy]
    })
  }

  return filters
})

// 方法
const handleFilterChange = (key, value) => {
  emit('filter-change', { [key]: value })
}

const handleRemoveFilter = (key) => {
  const resetValue = key === 'sortBy' ? 'relevance' : ''
  emit('filter-change', { [key]: resetValue })
}

const handleReset = () => {
  emit('reset-filters')
}
</script>

<style scoped>
.filters-section {
  margin-bottom: 32px;
}

.filters-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
}

/* 搜索信息 */
.search-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f6f8fa;
}

.search-keyword {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #24292f;
  font-size: 16px;
}

.search-keyword .el-icon {
  color: #007AFF;
}

.search-result {
  color: #656d76;
  font-size: 14px;
}

.search-result strong {
  color: #007AFF;
  font-weight: 600;
}

/* 筛选器行 */
.filters-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
}

.filters-group {
  display: flex;
  gap: 20px;
  flex: 1;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 140px;
}

.filter-label {
  font-size: 12px;
  color: #656d76;
  font-weight: 500;
}

.filter-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

/* 活跃筛选标签 */
.active-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f6f8fa;
  flex-wrap: wrap;
}

.filters-label {
  font-size: 12px;
  color: #656d76;
  font-weight: 500;
  flex-shrink: 0;
}

.filter-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tag:hover {
  background: #e3f2fd;
  border-color: #007AFF;
}

/* 响应式 */
@media (max-width: 1024px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .filters-group {
    flex-direction: column;
    gap: 16px;
  }

  .filter-item {
    min-width: auto;
  }

  .filter-actions {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .filters-container {
    padding: 16px;
  }

  .search-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .filters-group {
    gap: 12px;
  }

  .filter-actions {
    width: 100%;
    justify-content: stretch;
  }

  .filter-actions .el-button {
    flex: 1;
  }

  .active-filters {
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .filter-actions {
    flex-direction: column;
  }
}
</style>
