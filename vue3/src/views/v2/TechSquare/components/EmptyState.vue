<template>
  <div class="empty-state">
    <div class="empty-container">
      <!-- 图标 -->
      <div class="empty-icon">
        {{ iconMap[type] }}
      </div>

      <!-- 标题 -->
      <h3 class="empty-title">{{ titleMap[type] }}</h3>

      <!-- 描述 -->
      <p class="empty-description">{{ descriptionText }}</p>

      <!-- 操作按钮 -->
      <div class="empty-actions">
        <el-button
          v-if="type === 'error'"
          type="primary"
          @click="$emit('retry')"
          size="large"
        >
          重新加载
        </el-button>

        <el-button
          v-if="type === 'search'"
          type="primary"
          @click="$emit('clear-search')"
          size="large"
        >
          清空搜索
        </el-button>

        <el-button
          v-if="type === 'normal'"
          @click="goToDocumentManager"
          size="large"
        >
          去发布文档
        </el-button>
      </div>

      <!-- 建议 -->
      <div v-if="suggestions.length > 0" class="empty-suggestions">
        <p class="suggestions-title">{{ suggestionsTitle }}</p>
        <div class="suggestions-list">
          <el-tag
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="$emit('search-suggestion', suggestion)"
            class="suggestion-tag"
          >
            {{ suggestion }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

// Props
const props = defineProps({
  type: {
    type: String,
    default: 'normal', // 'normal' | 'search' | 'error'
    validator: (value) => ['normal', 'search', 'error'].includes(value)
  },
  keyword: {
    type: String,
    default: ''
  }
})

// Emits
defineEmits(['retry', 'clear-search', 'search-suggestion'])

const router = useRouter()

// 图标映射
const iconMap = {
  normal: '📚',
  search: '🔍',
  error: '😵'
}

// 标题映射
const titleMap = {
  normal: '暂无文档',
  search: '没有找到相关文档',
  error: '加载失败'
}

// 描述文本
const descriptionText = computed(() => {
  switch (props.type) {
    case 'search':
      return props.keyword
        ? `没有找到包含"${props.keyword}"的文档，试试其他关键词吧`
        : '没有找到相关文档，试试其他关键词吧'
    case 'error':
      return '网络连接异常或服务暂时不可用，请稍后重试'
    default:
      return '技术广场还没有文档，快去发布第一篇文档吧！'
  }
})

// 搜索建议
const suggestions = computed(() => {
  if (props.type !== 'search') return []

  return [
    'Vue3', 'React', 'JavaScript', 'TypeScript', 'Node.js',
    'Python', 'FastAPI', 'Docker', 'MySQL', 'Linux'
  ]
})

const suggestionsTitle = computed(() => {
  return props.type === 'search' ? '试试这些热门关键词：' : ''
})

// 方法
const goToDocumentManager = () => {
  router.push('/document-manager')
}
</script>

<style scoped>
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 40px 20px;
}

.empty-container {
  text-align: center;
  max-width: 500px;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 24px;
  opacity: 0.8;
}

.empty-title {
  font-size: 24px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 16px 0;
}

.empty-description {
  font-size: 16px;
  color: #656d76;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 32px;
}

/* 搜索建议 */
.empty-suggestions {
  background: #f6f8fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e1e4e8;
}

.suggestions-title {
  font-size: 14px;
  color: #656d76;
  margin: 0 0 16px 0;
  font-weight: 500;
}

.suggestions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #d0d7de;
  background: white;
}

.suggestion-tag:hover {
  background: #e3f2fd;
  border-color: #007AFF;
  color: #007AFF;
  transform: translateY(-1px);
}

/* 响应式 */
@media (max-width: 768px) {
  .empty-state {
    min-height: 300px;
    padding: 20px;
  }

  .empty-icon {
    font-size: 60px;
    margin-bottom: 16px;
  }

  .empty-title {
    font-size: 20px;
  }

  .empty-description {
    font-size: 14px;
  }

  .empty-actions {
    flex-direction: column;
    align-items: center;
  }

  .empty-actions .el-button {
    width: 100%;
    max-width: 200px;
  }

  .empty-suggestions {
    padding: 16px;
  }
}

/* 动画效果 */
.empty-container {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggestion-tag {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
