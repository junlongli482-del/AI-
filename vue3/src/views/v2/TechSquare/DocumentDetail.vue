<template>
  <div class="document-detail">
    <!-- 全局导航 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 面包屑导航 -->
      <div class="breadcrumb-section">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>
            <router-link to="/tech-square">技术广场</router-link>
          </el-breadcrumb-item>
          <el-breadcrumb-item>文档详情</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <el-result
          icon="error"
          title="加载失败"
          :sub-title="error"
        >
          <template #extra>
            <el-button type="primary" @click="loadDocument">重新加载</el-button>
            <el-button @click="goBack">返回列表</el-button>
          </template>
        </el-result>
      </div>

      <!-- 文档内容 -->
      <div v-else-if="documentData" class="document-container">
        <!-- 文档头部信息 -->
        <div class="document-header">
          <div class="file-type-badge">
            {{ getFileTypeIcon(documentData.file_type) }} {{ getFileTypeText(documentData.file_type) }}
          </div>
          <h1 class="document-title">{{ documentData.title }}</h1>
          <div class="document-meta">
            <span class="meta-item author-info">
              <span class="author-avatar">👤</span>
              <span class="author-name">{{ getAuthorDisplayName(documentData) }}</span>
              <span v-if="documentData.nickname && documentData.username !== documentData.nickname"
                    class="author-username">@{{ documentData.username }}</span>
            </span>
            <span class="meta-item">
              📅 {{ formatTime(documentData.publish_time) }}
            </span>
            <span class="meta-item">
              👀 {{ formatViewCount(documentData.view_count) }}
            </span>
            <span v-if="documentData.is_featured" class="featured-badge">
              ⭐ 推荐
            </span>
          </div>
        </div>

        <!-- 文档内容区域 -->
        <div class="document-content">
          <!-- MD文档渲染 -->
          <div v-if="documentData.file_type === 'md'" class="markdown-content">
            <!-- MD操作栏 -->
            <div class="actions-bar">
              <el-button @click="downloadMarkdown" type="primary" plain>
                📥 下载MD
              </el-button>
              <el-button @click="copyMarkdown" plain>
                📋 复制内容
              </el-button>
              <el-button @click="toggleRawContent" plain>
                {{ showRawContent ? '📖 查看渲染' : '📝 查看源码' }}
              </el-button>
            </div>

            <!-- 内容显示 -->
            <div v-if="!showRawContent" v-html="renderedContent" class="markdown-body"></div>
            <div v-else class="raw-content">
              <pre><code>{{ documentData.content }}</code></pre>
            </div>
          </div>

          <!-- PDF文档显示 -->
          <div v-else-if="documentData.file_type === 'pdf'" class="pdf-content">
            <!-- PDF操作栏 -->
            <div class="actions-bar">
              <el-button @click="downloadPDF" type="primary">
                📥 下载PDF
              </el-button>
              <el-button @click="openPDFNewTab" plain>
                🔗 新窗口打开
              </el-button>
            </div>

            <!-- PDF预览 -->
            <div class="pdf-viewer">
              <iframe
                :src="pdfUrl"
                class="pdf-iframe"
                frameborder="0"
                title="PDF文档预览"
              >
                <div class="pdf-fallback">
                  <p>您的浏览器不支持PDF预览</p>
                  <el-button @click="downloadPDF" type="primary">点击下载PDF</el-button>
                </div>
              </iframe>
            </div>
          </div>
        </div>

        <!-- 返回按钮 -->
        <div class="action-section">
          <el-button @click="goBack" size="large">
            ← 返回技术广场
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import AppHeader from '@/components/layout/AppHeader.vue'
import {
  getDocumentDetail,
  incrementViewCount,
  formatTime,
  formatViewCount,
  getFileTypeIcon,
  getFileTypeText
} from '@/api/v2/tech_square'

const route = useRoute()
const router = useRouter()

// ==================== 响应式数据 ====================
const loading = ref(false)
const error = ref('')
const documentData = ref(null)
const showRawContent = ref(false)

// ==================== 计算属性 ====================
const renderedContent = computed(() => {
  if (!documentData.value || documentData.value.file_type !== 'md') return ''

  try {
    marked.setOptions({
      highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return hljs.highlight(code, { language: lang }).value
          } catch (err) {
            console.error('代码高亮失败:', err)
          }
        }
        return hljs.highlightAuto(code).value
      },
      breaks: true,
      gfm: true
    })

    return marked(documentData.value.content || '')
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return '<p>内容渲染失败</p>'
  }
})

// PDF预览URL
const pdfUrl = computed(() => {
  if (!documentData.value) return ''
  const baseUrl = 'http://localhost:8100/api'
  return `${baseUrl}/v2/tech_square/documents/${documentData.value.id}/stream`
})

// ==================== 生命周期 ====================
onMounted(() => {
  loadDocument()
})

// ==================== 方法 ====================

/**
 * 获取作者显示名称
 */
const getAuthorDisplayName = (doc) => {
  if (!doc) return '未知作者'
  return doc.nickname || doc.username || `用户${doc.user_id}`
}

/**
 * 加载文档详情
 */
const loadDocument = async () => {
  const documentId = route.params.id
  if (!documentId) {
    error.value = '文档ID无效'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await getDocumentDetail(documentId)
    documentData.value = response

    // 增加浏览量
    try {
      await incrementViewCount(documentId)
      if (documentData.value) {
        documentData.value.view_count = (documentData.value.view_count || 0) + 1
      }
    } catch (viewError) {
      console.warn('增加浏览量失败:', viewError)
    }

  } catch (err) {
    console.error('加载文档详情失败:', err)
    if (err.response?.status === 404) {
      error.value = '文档不存在或已被删除'
    } else {
      error.value = '加载文档失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

/**
 * 在新窗口打开PDF
 */
const openPDFNewTab = () => {
  if (!documentData.value) return

  const baseUrl = 'http://localhost:8100/api'
  const url = `${baseUrl}/v2/tech_square/documents/${documentData.value.id}/stream`
  window.open(url, '_blank')
  ElMessage.success('正在新标签页中打开PDF')
}

/**
 * 下载PDF文档
 */
const downloadPDF = () => {
  if (!documentData.value) return

  const baseUrl = 'http://localhost:8100/api'
  const url = `${baseUrl}/v2/tech_square/documents/${documentData.value.id}/download`

  const link = window.document.createElement('a')
  link.href = url
  link.download = `${documentData.value.title}.pdf`
  link.target = '_blank'

  window.document.body.appendChild(link)
  link.click()
  window.document.body.removeChild(link)

  ElMessage.success('开始下载PDF文档')
}

/**
 * 下载Markdown文件
 */
const downloadMarkdown = () => {
  if (!documentData.value) return

  const baseUrl = 'http://localhost:8100/api'
  const url = `${baseUrl}/v2/tech_square/documents/${documentData.value.id}/download`

  const link = window.document.createElement('a')
  link.href = url
  link.download = `${documentData.value.title}.md`
  link.target = '_blank'

  window.document.body.appendChild(link)
  link.click()
  window.document.body.removeChild(link)

  ElMessage.success('开始下载MD文档')
}

/**
 * 复制Markdown内容
 */
const copyMarkdown = async () => {
  if (!documentData.value || !documentData.value.content) return

  try {
    await navigator.clipboard.writeText(documentData.value.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textArea = window.document.createElement('textarea')
    textArea.value = documentData.value.content
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    window.document.body.appendChild(textArea)
    textArea.select()
    window.document.execCommand('copy')
    window.document.body.removeChild(textArea)

    ElMessage.success('内容已复制到剪贴板')
  }
}

/**
 * 切换显示模式
 */
const toggleRawContent = () => {
  showRawContent.value = !showRawContent.value
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.push('/tech-square')
}
</script>

<style scoped>
.document-detail {
  min-height: 100vh;
  background: #fafbfc;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 面包屑 */
.breadcrumb-section {
  margin-bottom: 24px;
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #656d76;
}

:deep(.el-breadcrumb__item:not(:last-child) .el-breadcrumb__inner:hover) {
  color: #007AFF;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  padding: 40px 0;
}

/* 文档容器 */
.document-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
  overflow: hidden;
}

/* 文档头部 */
.document-header {
  padding: 32px;
  border-bottom: 1px solid #e1e4e8;
  background: #fafbfc;
}

.file-type-badge {
  display: inline-block;
  background: #e3f2fd;
  color: #007AFF;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 16px;
}

.document-title {
  font-size: 32px;
  font-weight: 700;
  color: #24292f;
  margin: 0 0 16px 0;
  line-height: 1.3;
}

.document-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  align-items: center;
}

.meta-item {
  color: #656d76;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.author-info {
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  color: #24292f !important;
  gap: 8px;
}

.author-name {
  font-weight: 600;
  color: #24292f;
}

.author-username {
  font-size: 12px;
  color: #656d76;
}

.featured-badge {
  background: #fff3cd;
  color: #856404;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

/* 文档内容 */
.document-content {
  padding: 32px;
}

/* 操作栏 */
.actions-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  flex-wrap: wrap;
}

/* Markdown内容 */
.markdown-content {
  max-width: none;
}

.markdown-body {
  font-size: 16px;
  line-height: 1.6;
  color: #24292f;
}

/* 原始内容 */
.raw-content {
  background: #f6f8fa;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
  overflow: hidden;
}

.raw-content pre {
  margin: 0;
  padding: 20px;
  background: none;
  border: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #24292f;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.raw-content code {
  background: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

/* PDF内容 */
.pdf-content {
  padding: 0;
}

.pdf-viewer {
  width: 100%;
  height: 800px;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
}

.pdf-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  text-align: center;
  color: #656d76;
}

/* GitHub风格Markdown样式 */
:deep(.markdown-body) {
  h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
    color: #24292f;
  }

  h1 { font-size: 2em; border-bottom: 1px solid #e1e4e8; padding-bottom: 8px; }
  h2 { font-size: 1.5em; border-bottom: 1px solid #e1e4e8; padding-bottom: 8px; }
  h3 { font-size: 1.25em; }

  p { margin-top: 0; margin-bottom: 16px; }

  ul, ol { margin-top: 0; margin-bottom: 16px; padding-left: 2em; }

  code {
    background: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 85%;
    color: #e36209;
  }

  pre {
    background: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    margin-bottom: 16px;
    border: 1px solid #e1e4e8;
  }

  pre code {
    background: none;
    padding: 0;
    color: inherit;
    font-size: 100%;
  }

  table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
  }

  th, td {
    border: 1px solid #e1e4e8;
    padding: 8px 12px;
    text-align: left;
  }

  th {
    background: #f6f8fa;
    font-weight: 600;
  }

  blockquote {
    margin: 0 0 16px 0;
    padding: 0 16px;
    color: #656d76;
    border-left: 4px solid #e1e4e8;
  }

  a {
    color: #007AFF;
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }

  img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    margin: 16px 0;
  }

  hr {
    border: none;
    border-top: 1px solid #e1e4e8;
    margin: 24px 0;
  }
}

/* 操作区域 */
.action-section {
  padding: 24px 32px;
  border-top: 1px solid #e1e4e8;
  background: #fafbfc;
}

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .document-header {
    padding: 20px;
  }

  .document-title {
    font-size: 24px;
  }

  .document-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .author-info {
    width: 100%;
  }

  .document-content {
    padding: 20px;
  }

  .actions-bar {
    flex-direction: column;
    gap: 8px;
  }

  .actions-bar .el-button {
    width: 100%;
  }

  .pdf-viewer {
    height: 600px;
  }

  .action-section {
    padding: 16px 20px;
  }

  :deep(.markdown-body) {
    font-size: 14px;
  }

  .raw-content pre {
    padding: 12px;
    font-size: 12px;
  }
}
</style>
