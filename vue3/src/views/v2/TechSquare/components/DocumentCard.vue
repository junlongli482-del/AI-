<template>
  <div
    class="document-card"
    @click="$emit('click')"
  >
    <div class="card-header">
      <div class="file-type-badge">
        {{ getFileTypeIcon(document.file_type) }} {{ getFileTypeText(document.file_type) }}
      </div>
      <div v-if="document.is_featured" class="featured-badge">
        ⭐ 推荐
      </div>
    </div>

    <div class="card-content">
      <h3 class="document-title">{{ document.title }}</h3>
      <p class="document-summary">{{ document.summary || '暂无摘要' }}</p>
    </div>

    <div class="card-footer">
      <div class="document-meta">
        <!-- ✅ 更新：显示作者信息 -->
        <span class="author-info">
          👤 {{ getAuthorDisplayName(document) }}
        </span>
        <span class="view-count">👀 {{ formatViewCount(document.view_count) }}</span>
        <span class="publish-time">{{ formatTime(document.publish_time) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  formatViewCount,
  formatTime,
  getFileTypeIcon,
  getFileTypeText
} from '@/api/v2/tech_square'

// Props
defineProps({
  document: {
    type: Object,
    required: true
  }
})

// Emits
defineEmits(['click'])

/**
 * ✅ 获取作者显示名称
 */
const getAuthorDisplayName = (doc) => {
  if (!doc) return '未知作者'

  // 优先显示昵称，如果没有昵称则显示用户名
  return doc.nickname || doc.username || `用户${doc.user_id}`
}
</script>

<style scoped>
.document-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e1e4e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.document-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.file-type-badge {
  background: #f6f8fa;
  color: #656d76;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.featured-badge {
  background: #fff3cd;
  color: #856404;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.card-content {
  flex: 1;
  margin-bottom: 16px;
}

.document-title {
  font-size: 18px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.document-summary {
  color: #656d76;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  border-top: 1px solid #e1e4e8;
  padding-top: 12px;
}

.document-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #656d76;
  flex-wrap: wrap;
  gap: 8px;
}

/* ✅ 新增：作者信息样式 */
.author-info {
  font-weight: 500;
  color: #24292f;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.view-count,
.publish-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 响应式 */
@media (max-width: 768px) {
  .document-card {
    padding: 16px;
  }

  .document-title {
    font-size: 16px;
  }

  .document-summary {
    font-size: 13px;
  }

  .document-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .author-info {
    width: 100%;
    text-align: center;
  }
}
</style>
