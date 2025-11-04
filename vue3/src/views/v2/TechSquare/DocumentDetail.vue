<template>
  <div class="document-detail">
    <!-- 全局导航 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 面包屑导航 -->
      <div class="breadcrumb-section">
        <div class="breadcrumb-nav">
          <router-link to="/tech-square" class="breadcrumb-link">
            <span class="breadcrumb-icon">🌟</span>
            <span class="breadcrumb-text">技术广场</span>
          </router-link>
          <span class="breadcrumb-separator">→</span>
          <span class="breadcrumb-current">文档详情</span>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="8" animated />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <div class="error-content">
          <div class="error-icon">😵</div>
          <h3 class="error-title">加载失败</h3>
          <p class="error-message">{{ error }}</p>
          <div class="error-actions">
            <el-button type="primary" @click="loadDocument">重新加载</el-button>
            <el-button @click="goBack">返回列表</el-button>
          </div>
        </div>
      </div>

      <!-- 文档内容 -->
      <div v-else-if="documentData" class="document-container">
        <!-- 文档头部 -->
        <div class="document-header">
          <div class="header-top">
            <div class="file-type-tag">
              <span class="type-icon">{{ getFileTypeIcon(documentData.file_type) }}</span>
              <span class="type-text">{{ getFileTypeText(documentData.file_type) }}</span>
            </div>
            <div v-if="documentData.is_featured" class="featured-tag">
              <span class="featured-icon">⭐</span>
              <span class="featured-text">推荐</span>
            </div>
          </div>

          <h1 class="document-title">{{ documentData.title }}</h1>

          <div class="document-meta">
            <div class="author-card">
              <div class="author-avatar">{{ getAuthorAvatar() }}</div>
              <div class="author-info">
                <div class="author-name">{{ getAuthorDisplayName(documentData) }}</div>
                <div class="publish-time">{{ formatTime(documentData.publish_time) }}</div>
              </div>
            </div>

            <div class="doc-stats">
              <div class="stat-item">
                <span class="stat-icon">👀</span>
                <span class="stat-text">{{ formatViewCount(documentData.view_count) }}</span>
              </div>
            </div>
          </div>

          <!-- 互动按钮 -->
          <div class="interaction-bar">
            <LikeButton
              :document-id="documentData.id"
              :initial-liked="interactionStats.is_liked || false"
              :initial-count="interactionStats.like_count || 0"
              @like-change="handleLikeChange"
              @login-required="handleLoginRequired"
            />
            <FavoriteButton
              :document-id="documentData.id"
              :initial-favorited="interactionStats.is_favorited || false"
              :initial-count="interactionStats.favorite_count || 0"
              @favorite-change="handleFavoriteChange"
              @login-required="handleLoginRequired"
            />
            <div class="comment-btn">
              <span class="btn-icon">💬</span>
              <span class="btn-text">{{ formatInteractionCount(interactionStats.comment_count || 0) }}</span>
            </div>
            <ShareButton
              :document-id="documentData.id"
              :document-title="documentData.title"
              :author-name="getAuthorDisplayName(documentData)"
              @share-success="handleShareSuccess"
            />
          </div>
        </div>

        <!-- 文档内容区域 -->
        <div class="document-body">
          <!-- MD文档 -->
          <div v-if="documentData.file_type === 'md'" class="markdown-section">
            <div class="content-toolbar">
              <el-button @click="downloadMarkdown" type="primary" size="small">
                📥 下载
              </el-button>
              <el-button @click="copyMarkdown" size="small">
                📋 复制
              </el-button>
              <el-button @click="toggleRawContent" size="small">
                {{ showRawContent ? '📖 渲染' : '📝 源码' }}
              </el-button>
            </div>

            <div v-if="!showRawContent" v-html="renderedContent" class="markdown-content"></div>
            <div v-else class="raw-content">
              <pre><code>{{ documentData.content }}</code></pre>
            </div>
          </div>

          <!-- PDF文档 -->
          <div v-else-if="documentData.file_type === 'pdf'" class="pdf-section">
            <div class="content-toolbar">
              <el-button @click="downloadPDF" type="primary" size="small">
                📥 下载PDF
              </el-button>
              <el-button @click="openPDFNewTab" size="small">
                🔗 新窗口
              </el-button>
            </div>

            <div class="pdf-viewer">
              <iframe
                :src="pdfUrl"
                class="pdf-frame"
                frameborder="0"
                title="PDF预览"
              >
              </iframe>
            </div>
          </div>
        </div>

        <!-- 评论系统 -->
        <CommentSection
          :document-id="documentData.id"
          :document-author-id="documentData.author_id || documentData.user_id"
          :initial-comment-count="interactionStats.comment_count || 0"
          @comment-count-change="handleCommentCountChange"
          @login-required="handleLoginRequired"
        />

        <!-- 底部操作 -->
        <div class="document-footer">
          <el-button @click="goBack" size="large" class="back-btn">
            <span class="back-icon">←</span>
            <span class="back-text">返回技术广场</span>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 登录提示 -->
    <el-dialog
      v-model="showLoginDialog"
      title="需要登录"
      width="400px"
      center
    >
      <div class="login-prompt">
        <div class="login-icon">🔐</div>
        <p class="login-text">{{ loginMessage }}</p>
      </div>
      <template #footer>
        <el-button @click="showLoginDialog = false">取消</el-button>
        <el-button type="primary" @click="goToLogin">去登录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 在文件顶部添加导入
import { API_BASE_URL } from '@/utils/request'
import { ref, onMounted, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import AppHeader from '@/components/layout/AppHeader.vue'
import LikeButton from './components/LikeButton.vue'
import FavoriteButton from './components/FavoriteButton.vue'
import ShareButton from './components/ShareButton.vue'
import CommentSection from './components/CommentSection.vue'
import {
  getDocumentDetail,
  incrementViewCount,
  formatTime,
  formatViewCount,
  getFileTypeIcon,
  getFileTypeText
} from '@/api/v2/tech_square'
import {
  getLikeStatus,
  getFavoriteStatus,
  formatInteractionCount
} from '@/api/v2/interaction'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const error = ref('')
const documentData = ref(null)
const showRawContent = ref(false)
const showLoginDialog = ref(false)
const loginMessage = ref('')

const interactionStats = reactive({
  like_count: 0,
  favorite_count: 0,
  comment_count: 0,
  is_liked: false,
  is_favorited: false
})

// 计算属性
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

const pdfUrl = computed(() => {
  if (!documentData.value) return ''
  return `${API_BASE_URL}/v2/tech_square/documents/${documentData.value.id}/stream`
})

// 生命周期
onMounted(() => {
  loadDocument()
})

// 方法
const getAuthorAvatar = () => {
  const name = getAuthorDisplayName(documentData.value)
  return name.charAt(0).toUpperCase()
}

const getAuthorDisplayName = (doc) => {
  if (!doc) return '未知'
  return doc.nickname || doc.username || `用户${doc.user_id}`
}

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

    try {
      await incrementViewCount(documentId)
      if (documentData.value) {
        documentData.value.view_count = (documentData.value.view_count || 0) + 1
      }
    } catch (viewError) {
      console.warn('增加浏览量失败:', viewError)
    }

    await loadInteractionStats(documentId)
  } catch (err) {
    console.error('加载文档失败:', err)
    if (err.response?.status === 404) {
      error.value = '文档不存在或已被删除'
    } else {
      error.value = '加载文档失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

const loadInteractionStats = async (documentId) => {
  try {
    const [likeStatus, favoriteStatus] = await Promise.all([
      getLikeStatus(documentId),
      getFavoriteStatus(documentId)
    ])

    Object.assign(interactionStats, {
      like_count: likeStatus.like_count || 0,
      favorite_count: favoriteStatus.favorite_count || 0,
      comment_count: 0,
      is_liked: likeStatus.is_liked || false,
      is_favorited: favoriteStatus.is_favorited || false
    })
  } catch (error) {
    console.warn('加载互动统计失败:', error)
    Object.assign(interactionStats, {
      like_count: 0,
      favorite_count: 0,
      comment_count: 0,
      is_liked: false,
      is_favorited: false
    })
  }
}

const handleLikeChange = (data) => {
  interactionStats.is_liked = data.isLiked
  interactionStats.like_count = data.likeCount
}

const handleFavoriteChange = (data) => {
  interactionStats.is_favorited = data.isFavorited
  interactionStats.favorite_count = data.favoriteCount
}

const handleCommentCountChange = (newCount) => {
  interactionStats.comment_count = newCount
}

const handleLoginRequired = (actionData) => {
  if (typeof actionData === 'string') {
    loginMessage.value = actionData
  } else {
    if (actionData.type === 'like') {
      loginMessage.value = '需要登录才能点赞文档'
    } else if (actionData.type === 'favorite') {
      loginMessage.value = '需要登录才能收藏文档'
    } else {
      loginMessage.value = '需要登录才能进行此操作'
    }
  }
  showLoginDialog.value = true
}

const goToLogin = () => {
  showLoginDialog.value = false
  const currentPath = route.fullPath
  router.push(`/login?redirect=${encodeURIComponent(currentPath)}`)
}

const handleShareSuccess = (data) => {
  console.log('分享成功:', data)
}

const downloadMarkdown = () => {
  if (!documentData.value) return
  const url = `${API_BASE_URL}/v2/tech_square/documents/${documentData.value.id}/download`

  const link = document.createElement('a')
  link.href = url
  link.download = `${documentData.value.title}.md`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success('开始下载')
}

const copyMarkdown = async () => {
  if (!documentData.value?.content) return

  try {
    await navigator.clipboard.writeText(documentData.value.content)
    ElMessage.success('内容已复制')
  } catch (error) {
    const textArea = document.createElement('textarea')
    textArea.value = documentData.value.content
    textArea.style.position = 'fixed'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('内容已复制')
  }
}

const toggleRawContent = () => {
  showRawContent.value = !showRawContent.value
}

const downloadPDF = () => {
  if (!documentData.value) return
  const url = `${API_BASE_URL}/v2/tech_square/documents/${documentData.value.id}/download`

  const link = document.createElement('a')
  link.href = url
  link.download = `${documentData.value.title}.pdf`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success('开始下载')
}

const openPDFNewTab = () => {
  if (!documentData.value) return
  window.open(pdfUrl.value, '_blank')
  ElMessage.success('正在新标签页中打开')
}

const goBack = () => {
  router.push('/tech-square')
}
</script>

<style scoped>
.document-detail {
  min-height: 100vh;
  background: linear-gradient(135deg,
  rgba(255, 154, 158, 0.1) 0%,
  rgba(250, 208, 196, 0.1) 25%,
  rgba(168, 237, 234, 0.1) 50%,
  rgba(254, 214, 227, 0.1) 75%,
  rgba(255, 234, 167, 0.1) 100%
  );
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* 面包屑 */
.breadcrumb-section {
  margin-bottom: 32px;
}

.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #007AFF;
  font-weight: 500;
  transition: all 0.3s ease;
}

.breadcrumb-link:hover {
  color: #4A90E2;
}

.breadcrumb-separator {
  color: #86868b;
  font-size: 14px;
}

.breadcrumb-current {
  color: #86868b;
  font-weight: 500;
}

/* 状态页面 */
.loading-state,
.error-state {
  padding: 60px 20px;
  text-align: center;
}

.error-content {
  max-width: 400px;
  margin: 0 auto;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 16px 0;
}

.error-message {
  font-size: 16px;
  color: #86868b;
  margin: 0 0 32px 0;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 文档容器 */
.document-container {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 文档头部 */
.document-header {
  padding: 40px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.file-type-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 122, 255, 0.1);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: #007AFF;
}

.featured-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: #856404;
}

.document-title {
  font-size: 36px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 32px 0;
  line-height: 1.2;
}

.document-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.author-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

.author-name {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 4px;
}

.publish-time {
  font-size: 14px;
  color: #86868b;
}

.doc-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #86868b;
}

.stat-icon {
  font-size: 16px;
}

/* 互动栏 */
.interaction-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 24px 0 0 0;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.comment-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #86868b;
}

/* 文档主体 */
.document-body {
  padding: 40px;
}

.content-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  padding: 16px 20px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

/* Markdown内容 */
.markdown-content {
  font-size: 16px;
  line-height: 1.7;
  color: #1d1d1f;
}

.raw-content {
  background: rgba(248, 250, 252, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.raw-content pre {
  margin: 0;
  padding: 24px;
  background: none;
  border: none;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #1d1d1f;
  overflow-x: auto;
  white-space: pre-wrap;
}

/* PDF查看器 */
.pdf-viewer {
  width: 100%;
  height: 800px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.pdf-frame {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #86868b;
}

/* 文档底部 */
.document-footer {
  padding: 32px 40px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  border-radius: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.3);
}

/* 登录提示 */
.login-prompt {
  text-align: center;
  padding: 20px 0;
}

.login-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.login-text {
  color: #86868b;
  margin: 0;
  font-size: 16px;
}

/* Markdown样式 */
:deep(.markdown-content) {
  h1, h2, h3, h4, h5, h6 {
    margin-top: 32px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
    color: #1d1d1f;
  }

  h1 { font-size: 2em; }
  h2 { font-size: 1.5em; }
  h3 { font-size: 1.25em; }

  p { margin-bottom: 16px; }

  code {
    background: rgba(0, 122, 255, 0.1);
    padding: 2px 6px;
    border-radius: 6px;
    font-size: 85%;
    color: #007AFF;
  }

  pre {
    background: rgba(248, 250, 252, 0.8);
    padding: 20px;
    border-radius: 12px;
    overflow-x: auto;
    margin-bottom: 16px;
    border: 1px solid rgba(0, 0, 0, 0.06);
  }

  pre code {
    background: none;
    padding: 0;
    color: inherit;
  }

  blockquote {
    margin: 16px 0;
    padding: 0 20px;
    color: #86868b;
    border-left: 4px solid #007AFF;
  }

  a {
    color: #007AFF;
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .main-content {
    padding: 20px 16px;
  }

  .document-header,
  .document-body,
  .document-footer {
    padding: 24px 20px;
  }

  .document-title {
    font-size: 28px;
  }

  .document-meta {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .interaction-bar {
    flex-wrap: wrap;
    gap: 12px;
  }

  .content-toolbar {
    flex-direction: column;
    gap: 8px;
  }

  .pdf-viewer {
    height: 600px;
  }

  .back-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
