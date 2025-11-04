<template>
  <div class="document-list-container">
    <!-- Tab切换 -->
    <el-tabs v-model="activeTab" class="list-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="我的文档" name="documents">
        <!-- 头部：统计信息 -->
        <div class="list-header">
          <div class="stats-bar">
            <div class="stat-item">
              <span class="stat-label">总文档：</span>
              <span class="stat-value">{{ stats.total_documents || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">草稿：</span>
              <span class="stat-value">{{ stats.documents_by_status?.draft || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已发布：</span>
              <span class="stat-value">{{ stats.documents_by_status?.published || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">审核中：</span>
              <span class="stat-value">{{ pendingReviewCount }}</span>
            </div>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="handleUpload" :icon="Upload">
              上传文件
            </el-button>
            <el-button @click="showCreateDialog" :icon="Plus">
              新建文档
            </el-button>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <!-- 文档列表 -->
        <div v-else-if="documents.length > 0" class="document-list">
          <div
            v-for="doc in documents"
            :key="doc.id"
            class="document-item"
            @click="showDetail(doc)"
          >
            <div class="doc-info">
              <div class="doc-header">
                <span class="doc-icon">{{ getFileIcon(doc.file_type) }}</span>
                <h4 class="doc-title">{{ doc.title }}</h4>

                <!-- 使用新的状态显示组件 -->
                <PublishStatus
                  :document="doc"
                  :show-refresh="true"
                  @status-updated="handleStatusUpdated"
                  @retry-review="handleRetryReview"
                />
              </div>

              <div class="doc-meta">
                <span class="meta-item">
                  📁 {{ doc.folder_name || '根目录' }}
                </span>
                <span class="meta-item">
                  📏 {{ formatFileSize(doc.file_size) }}
                </span>
                <span class="meta-item">
                  🕐 {{ formatDate(doc.updated_at) }}
                </span>
              </div>
            </div>

            <div class="doc-actions" @click.stop>
              <!-- 发布相关按钮 -->
              <div class="publish-actions">
                <!-- 草稿状态：显示发布按钮 -->
                <el-button
                  v-if="canPublish(doc.status)"
                  type="primary"
                  size="small"
                  @click="handlePublish(doc)"
                  :loading="publishingDocs.has(doc.id)"
                >
                  {{ getPublishButtonText(doc) }}
                </el-button>

                <!-- 审核失败状态：显示重新发布按钮 -->
                <el-button
                  v-if="doc.status === 'review_failed'"
                  type="primary"
                  size="small"
                  @click="handlePublish(doc)"
                  :loading="publishingDocs.has(doc.id)"
                >
                  重新发布
                </el-button>

                <!-- 已发布状态：显示更新发布和取消发布按钮 -->
                <template v-if="doc.status === 'published'">
                  <el-button
                    type="primary"
                    size="small"
                    @click="handleUpdatePublish(doc)"
                    :loading="publishingDocs.has(doc.id)"
                  >
                    更新发布
                  </el-button>
                  <el-button
                    type="danger"
                    size="small"
                    @click="handleUnpublish(doc)"
                    :loading="unpublishingDocs.has(doc.id)"
                  >
                    取消发布
                  </el-button>
                </template>
              </div>

              <!-- 基础操作按钮 -->
              <div class="basic-actions">
                <el-button
                  type="text"
                  size="small"
                  @click="editDocument(doc)"
                >
                  {{ getActionButtonText(doc.file_type) }}
                </el-button>
                <el-button
                  type="text"
                  size="small"
                  @click="deleteDocument(doc)"
                  class="delete-btn"
                >
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无文档">
            <el-button type="primary" @click="handleUpload">
              上传文件
            </el-button>
          </el-empty>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="上传历史" name="uploads">
        <!-- 上传历史内容 -->
        <UploadHistory @create-document="handleCreateFromUpload" />
      </el-tab-pane>
    </el-tabs>

    <!-- 文档详情对话框 -->
    <DocumentDetail
      v-model="detailDialogVisible"
      :document="currentDocument"
      @refresh="loadDocuments"
    />
  </div>
</template>

<script setup>
// 在文件顶部添加导入
import { API_BASE_URL } from '@/utils/request'
// 保持原有的所有逻辑不变
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Loading } from '@element-plus/icons-vue'
import {
  getDocuments,
  deleteDocument as deleteDocApi,
  formatFileSize
} from '@/api/v2/document_manager/index'
import {
  submitPublish,
  unpublishDocument,
  updatePublishedDocument,
  canPublish
} from '@/api/v2/document_publish/index'
import DocumentDetail from './DocumentDetail.vue'
import UploadHistory from './UploadHistory.vue'
import PublishStatus from './PublishStatus.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  folderId: {
    type: Number,
    default: null
  },
  stats: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['refresh-stats', 'open-upload'])

// 响应式数据
const activeTab = ref('documents')
const loading = ref(false)
const documents = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const detailDialogVisible = ref(false)
const currentDocument = ref(null)

// 发布相关状态
const publishingDocs = ref(new Set()) // 正在发布的文档ID集合
const unpublishingDocs = ref(new Set()) // 正在取消发布的文档ID集合
const pollingTimer = ref(null) // 轮询定时器

// 计算属性：审核中文档数量
const pendingReviewCount = computed(() => {
  return documents.value.filter(doc => doc.status === 'pending_review').length
})

// Tab切换处理
const handleTabChange = (tabName) => {
  if (tabName === 'documents') {
    loadDocuments()
  }
}

// 加载文档列表
const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    // 如果有选中文件夹，添加筛选条件
    if (props.folderId !== null) {
      params.folder_id = props.folderId
    }

    const data = await getDocuments(params)
    documents.value = data.documents
    total.value = data.total

    // 触发统计信息刷新
    emit('refresh-stats')

    // 启动轮询（如果有审核中的文档）
    startPolling()
  } catch (error) {
    ElMessage.error('加载文档列表失败')
    console.error('加载文档失败:', error)
  } finally {
    loading.value = false
  }
}

// 启动轮询检查审核状态
const startPolling = () => {
  // 清除现有定时器
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
  }

  // 检查是否有审核中的文档
  const hasPendingReview = documents.value.some(doc => doc.status === 'pending_review')

  if (hasPendingReview && activeTab.value === 'documents') {
    pollingTimer.value = setInterval(() => {
      checkPendingReviewStatus()
    }, 30000) // 30秒轮询一次
  }
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

// 检查审核中文档的状态
const checkPendingReviewStatus = async () => {
  const pendingDocs = documents.value.filter(doc => doc.status === 'pending_review')

  if (pendingDocs.length === 0) {
    stopPolling()
    return
  }

  console.log(`检查 ${pendingDocs.length} 个审核中文档的状态...`)

  // 逐个检查审核中文档的状态
  for (const doc of pendingDocs) {
    try {
      const { getReviewStatus } = await import('@/api/v2/ai_review/index')
      const statusData = await getReviewStatus(doc.id)

      // 根据审核状态更新文档状态
      let newStatus = doc.status
      if (statusData.overall_status === 'passed') {
        newStatus = 'published'
      } else if (statusData.overall_status === 'failed') {
        newStatus = 'review_failed'
      }

      // 如果状态有变化，更新本地状态
      if (newStatus !== doc.status) {
        console.log(`文档 ${doc.title} 状态更新: ${doc.status} → ${newStatus}`)

        const docIndex = documents.value.findIndex(d => d.id === doc.id)
        if (docIndex !== -1) {
          documents.value[docIndex].status = newStatus
        }

        // 显示状态更新提示
        ElMessage.success(`文档"${doc.title}"状态已更新为：${newStatus === 'published' ? '已发布' : '审核失败'}`)
      }

    } catch (error) {
      console.error(`检查文档 ${doc.id} 状态失败:`, error)
    }
  }

  // 刷新统计信息
  emit('refresh-stats')

  // 检查是否还有审核中的文档，没有则停止轮询
  const stillPending = documents.value.some(doc => doc.status === 'pending_review')
  if (!stillPending) {
    console.log('没有审核中文档，停止轮询')
    stopPolling()
  }
}

// 监听文件夹变化
watch(() => props.folderId, () => {
  currentPage.value = 1
  if (activeTab.value === 'documents') {
    loadDocuments()
  }
}, { immediate: true })

// 监听Tab变化，控制轮询
watch(activeTab, (newTab) => {
  if (newTab === 'documents') {
    startPolling()
  } else {
    stopPolling()
  }
})

// 分页处理
const handlePageChange = () => {
  loadDocuments()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadDocuments()
}

// 发布相关方法
const handlePublish = async (doc) => {
  publishingDocs.value.add(doc.id)

  try {
    await submitPublish({
      document_id: doc.id,
      publish_reason: `发布文档：${doc.title}`
    })

    ElMessage.success('文档已提交发布，正在AI审核中...')

    // 更新文档状态
    const docIndex = documents.value.findIndex(d => d.id === doc.id)
    if (docIndex !== -1) {
      documents.value[docIndex].status = 'pending_review'
    }

    // 启动轮询
    startPolling()

    // 刷新统计
    emit('refresh-stats')

  } catch (error) {
    console.error('发布失败:', error)
    ElMessage.error(error.response?.data?.detail || '发布失败')
  } finally {
    publishingDocs.value.delete(doc.id)
  }
}

const handleUpdatePublish = async (doc) => {
  // 防重复点击保护
  if (publishingDocs.value.has(doc.id)) {
    return
  }

  console.log('=== 更新已发布文档 ===')

  publishingDocs.value.add(doc.id)

  try {
    // 先获取文档详情，获取当前内容
    const { getDocumentDetail } = await import('@/api/v2/document_manager/index')
    const docDetail = await getDocumentDetail(doc.id)

    // 发送完整的内容数据
    const updateData = {
      title: docDetail.title,
      content: docDetail.content,
      summary: docDetail.summary,
      update_reason: `更新发布：${doc.title}`
    }

    const result = await updatePublishedDocument(doc.id, updateData)
    console.log('更新成功:', result)

    ElMessage.success('文档已提交更新，正在AI审核中...')

    // 更新文档状态为审核中
    const docIndex = documents.value.findIndex(d => d.id === doc.id)
    if (docIndex !== -1) {
      documents.value[docIndex].status = 'pending_review'
    }

    // 启动轮询
    startPolling()

    // 刷新统计
    emit('refresh-stats')

  } catch (error) {
    console.error('更新发布失败:', error)
    const errorMsg = error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      '更新发布失败'

    ElMessage.error(`更新发布失败: ${errorMsg}`)
  } finally {
    publishingDocs.value.delete(doc.id)
  }
}

const handleUnpublish = async (doc) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消发布文档"${doc.title}"吗？文档将从技术广场下架。`,
      '取消发布确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    unpublishingDocs.value.add(doc.id)

    await unpublishDocument(doc.id, '用户主动取消发布')

    ElMessage.success('文档已取消发布')

    // 更新文档状态
    const docIndex = documents.value.findIndex(d => d.id === doc.id)
    if (docIndex !== -1) {
      documents.value[docIndex].status = 'draft'
    }

    // 刷新统计
    emit('refresh-stats')

  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消发布失败:', error)
      ElMessage.error(error.response?.data?.detail || '取消发布失败')
    }
  } finally {
    unpublishingDocs.value.delete(doc.id)
  }
}

// 状态更新处理
const handleStatusUpdated = (event) => {
  const { documentId, newStatus } = event

  // 更新本地文档状态
  const docIndex = documents.value.findIndex(d => d.id === documentId)
  if (docIndex !== -1) {
    documents.value[docIndex].status = newStatus
  }

  // 刷新统计
  emit('refresh-stats')

  // 检查是否还需要轮询
  startPolling()
}

// 重新审核处理
const handleRetryReview = (event) => {
  const { documentId, newStatus } = event

  // 更新本地文档状态
  const docIndex = documents.value.findIndex(d => d.id === documentId)
  if (docIndex !== -1) {
    documents.value[docIndex].status = newStatus
  }

  // 启动轮询
  startPolling()

  // 刷新统计
  emit('refresh-stats')
}

// 获取发布按钮文本
const getPublishButtonText = (doc) => {
  if (doc.status === 'draft') return '发布'
  if (doc.status === 'review_failed') return '重新发布'
  if (doc.status === 'unpublished') return '重新发布'
  return '发布'
}


// 打开上传对话框
const handleUpload = () => {
  emit('open-upload')
}

// 显示创建对话框
const showCreateDialog = () => {
  const query = {}
  if (props.folderId !== null) {
    query.folder_id = props.folderId
  }

  router.push({
    path: '/document-editor',
    query
  })
}

// 显示文档详情
const showDetail = (doc) => {
  currentDocument.value = doc
  detailDialogVisible.value = true
}

// 编辑/查看文档
const editDocument = async (doc) => {
  if (doc.file_type === 'pdf') {
    try {
      const { getToken } = await import('@/utils/auth')
      const response = await fetch(`${API_BASE_URL}/v2/document_manager/documents/${doc.id}/stream`, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      })

      if (!response.ok) {
        throw new Error('获取PDF失败')
      }

      const blob = await response.blob()
      const pdfUrl = window.URL.createObjectURL(blob)
      window.open(pdfUrl, '_blank')

      setTimeout(() => {
        window.URL.revokeObjectURL(pdfUrl)
      }, 1000)

    } catch (error) {
      console.error('查看PDF失败:', error)
      ElMessage.error('查看PDF失败')
    }
  } else {
    // Markdown文档进入编辑器
    router.push({
      path: '/document-editor',
      query: { id: doc.id }
    })
  }
}

// 删除文档
const deleteDocument = async (doc) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档"${doc.title}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteDocApi(doc.id)
    ElMessage.success('文档删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
    }
  }
}

// 从上传历史创建文档
const handleCreateFromUpload = () => {
  // 切换到文档列表并刷新
  activeTab.value = 'documents'
  loadDocuments()
}

// 获取文件图标
const getFileIcon = (fileType) => {
  return fileType === 'pdf' ? '📕' : '📄'
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  // 小于24小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  // 超过7天显示具体日期
  return date.toLocaleDateString('zh-CN')
}

// 获取操作按钮文本
const getActionButtonText = (fileType) => {
  return fileType === 'pdf' ? '查看' : '编辑'
}

// 组件卸载时清理定时器
onUnmounted(() => {
  stopPolling()
})

// 暴露刷新方法
defineExpose({
  refresh: loadDocuments
})

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.document-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
}

/* Tab样式优化 */
.list-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-tabs__header) {
  margin: 0;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.el-tabs__nav-wrap) {
  padding: 0;
}

:deep(.el-tabs__item) {
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
  font-size: 15px;
  font-weight: 500;
  color: #86868b;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

:deep(.el-tabs__item.is-active) {
  color: #007AFF;
  border-bottom-color: #007AFF;
}

:deep(.el-tabs__item:hover) {
  color: #007AFF;
}

:deep(.el-tabs__active-bar) {
  background: #007AFF;
}

:deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

:deep(.el-tab-pane) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.list-header {
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.stats-bar {
  display: flex;
  gap: 24px;
}

.stat-item {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.stat-label {
  color: #86868b;
  font-weight: 500;
}

.stat-value {
  color: #1d1d1f;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #86868b;
  overflow: hidden;
}

.document-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px 24px;
}

.document-item {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.document-item:hover {
  transform: translateY(-2px);
  border-color: rgba(0, 122, 255, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.doc-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.doc-title {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #86868b;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.doc-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
  align-items: flex-end;
}

.publish-actions {
  display: flex;
  gap: 8px;
}

.basic-actions {
  display: flex;
  gap: 8px;
}

.delete-btn {
  color: #dc3545;
}

.delete-btn:hover {
  color: #dc3545;
  background: rgba(220, 53, 69, 0.1);
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  overflow: hidden;
}

.pagination-container {
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.5);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

/* 滚动条样式 */
.document-list::-webkit-scrollbar {
  width: 6px;
}

.document-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.document-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* Element Plus 按钮样式覆盖 */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  border: none;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

:deep(.el-button--danger) {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  border-color: rgba(220, 53, 69, 0.2);
}

:deep(.el-button--text) {
  color: #007AFF;
}

:deep(.el-button--text:hover) {
  background: rgba(0, 122, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-tabs__header) {
    padding: 0 16px;
  }

  :deep(.el-tabs__item) {
    padding: 0 16px;
  }

  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 16px;
  }

  .stats-bar {
    flex-wrap: wrap;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }

  .document-list {
    padding: 16px;
  }

  .document-item {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .doc-actions {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
  }

  .publish-actions,
  .basic-actions {
    flex-wrap: wrap;
  }
}
</style>
