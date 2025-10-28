<template>
  <div class="preview-panel">
    <div class="preview-header">
      <span class="preview-title">预览</span>
      <div class="preview-actions">
        <el-button size="small" text @click="scrollToTop">
          <el-icon><Top /></el-icon>
        </el-button>
      </div>
    </div>
    <div ref="previewRef" class="preview-content" v-html="renderedHtml"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import { Top } from '@element-plus/icons-vue'

const props = defineProps({
  content: {
    type: String,
    default: ''
  }
})

const previewRef = ref(null)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false
})

// 渲染 HTML
const renderedHtml = computed(() => {
  if (!props.content) {
    return '<div class="empty-content">暂无内容</div>'
  }

  try {
    return marked(props.content)
  } catch (error) {
    console.error('Markdown 渲染失败:', error)
    return '<div class="error-content">内容渲染失败</div>'
  }
})

// 滚动到顶部
const scrollToTop = () => {
  if (previewRef.value) {
    previewRef.value.scrollTop = 0
  }
}

// 监听内容变化，自动滚动到底部（可选）
watch(() => props.content, async () => {
  await nextTick()
  // 如果需要自动滚动到底部，取消注释下面的代码
  // if (previewRef.value) {
  //   previewRef.value.scrollTop = previewRef.value.scrollHeight
  // }
})
</script>

<style scoped>
.preview-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  overflow: hidden;
}

.preview-header {
  height: 48px;
  border-bottom: 1px solid #d0d7de;
  background: #f6f8fa;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #24292f;
}

.preview-actions {
  display: flex;
  gap: 4px;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
  line-height: 1.6;
  color: #24292f;
}

/* Markdown 样式 */
:deep(.preview-content h1) {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #d0d7de;
  color: #24292f;
}

:deep(.preview-content h2) {
  font-size: 24px;
  font-weight: 600;
  margin: 32px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #d0d7de;
  color: #24292f;
}

:deep(.preview-content h3) {
  font-size: 20px;
  font-weight: 600;
  margin: 24px 0 12px 0;
  color: #24292f;
}

:deep(.preview-content h4) {
  font-size: 16px;
  font-weight: 600;
  margin: 20px 0 12px 0;
  color: #24292f;
}

:deep(.preview-content h5) {
  font-size: 14px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #24292f;
}

:deep(.preview-content h6) {
  font-size: 13px;
  font-weight: 600;
  margin: 16px 0 8px 0;
  color: #656d76;
}

:deep(.preview-content p) {
  margin: 0 0 16px 0;
  color: #24292f;
}

:deep(.preview-content strong) {
  font-weight: 600;
  color: #24292f;
}

:deep(.preview-content em) {
  font-style: italic;
}

:deep(.preview-content del) {
  text-decoration: line-through;
  color: #656d76;
}

:deep(.preview-content a) {
  color: #007AFF;
  text-decoration: none;
}

:deep(.preview-content a:hover) {
  text-decoration: underline;
}

:deep(.preview-content ul),
:deep(.preview-content ol) {
  margin: 0 0 16px 0;
  padding-left: 24px;
}

:deep(.preview-content li) {
  margin: 4px 0;
}

:deep(.preview-content li > p) {
  margin: 0;
}

:deep(.preview-content blockquote) {
  margin: 16px 0;
  padding: 0 16px;
  border-left: 4px solid #d0d7de;
  color: #656d76;
  background: #f6f8fa;
}

:deep(.preview-content blockquote p) {
  margin: 8px 0;
}

:deep(.preview-content code) {
  background: #f6f8fa;
  color: #d73a49;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Source Code Pro', monospace;
  font-size: 85%;
}

:deep(.preview-content pre) {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Source Code Pro', monospace;
  font-size: 85%;
  line-height: 1.45;
}

:deep(.preview-content pre code) {
  background: transparent;
  color: #24292f;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

:deep(.preview-content table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  overflow: hidden;
}

:deep(.preview-content th),
:deep(.preview-content td) {
  padding: 8px 12px;
  border: 1px solid #d0d7de;
  text-align: left;
}

:deep(.preview-content th) {
  background: #f6f8fa;
  font-weight: 600;
  color: #24292f;
}

:deep(.preview-content tr:nth-child(even)) {
  background: #f6f8fa;
}

:deep(.preview-content hr) {
  height: 1px;
  background: #d0d7de;
  border: none;
  margin: 24px 0;
}

/* 空状态和错误状态 */
:deep(.empty-content) {
  text-align: center;
  color: #656d76;
  font-style: italic;
  padding: 48px 16px;
}

:deep(.error-content) {
  text-align: center;
  color: #f56c6c;
  padding: 48px 16px;
}

/* 滚动条样式 */
.preview-content::-webkit-scrollbar {
  width: 6px;
}

.preview-content::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.preview-content::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-content {
    padding: 16px;
  }

  :deep(.preview-content h1) {
    font-size: 24px;
  }

  :deep(.preview-content h2) {
    font-size: 20px;
  }

  :deep(.preview-content h3) {
    font-size: 18px;
  }

  :deep(.preview-content pre) {
    padding: 12px;
    font-size: 12px;
  }

  :deep(.preview-content table) {
    font-size: 12px;
  }

  :deep(.preview-content th),
  :deep(.preview-content td) {
    padding: 6px 8px;
  }
}
</style>
