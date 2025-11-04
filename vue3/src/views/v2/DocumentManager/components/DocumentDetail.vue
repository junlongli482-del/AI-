<template>
  <el-dialog
    v-model="dialogVisible"
    :title="document?.title || '文档详情'"
    width="800px"
    @close="handleClose"
  >
    <div v-if="document" class="document-detail">
      <!-- 基本信息 -->
      <div class="detail-section">
        <h4 class="section-title">基本信息</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">文档标题：</span>
            <span class="info-value">{{ document.title }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">文件类型：</span>
            <span class="info-value">{{ getFileTypeText(document.file_type) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">文件大小：</span>
            <span class="info-value">{{ formatFileSize(document.file_size) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">所属文件夹：</span>
            <span class="info-value">{{ document.folder_name || '根目录' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态：</span>
            <el-tag :type="getStatusType(document.status)" size="small">
              {{ getStatusText(document.status) }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间：</span>
            <span class="info-value">{{ formatDateTime(document.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">更新时间：</span>
            <span class="info-value">{{ formatDateTime(document.updated_at) }}</span>
          </div>
          <div v-if="document.publish_time" class="info-item">
            <span class="info-label">发布时间：</span>
            <span class="info-value">{{ formatDateTime(document.publish_time) }}</span>
          </div>
        </div>
      </div>

      <!-- 文档摘要 -->
      <div v-if="document.summary" class="detail-section">
        <h4 class="section-title">文档摘要</h4>
        <p class="summary-text">{{ document.summary }}</p>
      </div>

      <!-- 审核信息 -->
      <div v-if="document.review_message" class="detail-section">
        <h4 class="section-title">审核信息</h4>
        <el-alert
          :type="document.status === 'review_failed' ? 'error' : 'success'"
          :closable="false"
        >
          {{ document.review_message }}
        </el-alert>
      </div>

      <!-- 文档内容预览（仅MD） -->
      <div v-if="document.file_type === 'md' && document.content" class="detail-section">
        <h4 class="section-title">内容预览</h4>
        <div class="content-preview">
          {{ getPreviewContent(document.content) }}
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <!-- 只有Markdown文档才显示编辑按钮 -->
        <el-button
          v-if="document?.file_type === 'md'"
          type="primary"
          @click="editDocument"
        >
          编辑文档
        </el-button>
        <!-- PDF文档显示查看和下载按钮 -->
        <template v-else-if="document?.file_type === 'pdf'">
          <el-button @click="viewPdfDocument">
            <el-icon><View /></el-icon>
            查看PDF
          </el-button>
          <el-button type="primary" @click="downloadPdfDocument">
            <el-icon><Download /></el-icon>
            下载PDF
          </el-button>
        </template>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
// 在文件顶部添加导入
import { API_BASE_URL } from '@/utils/request'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { View, Download } from '@element-plus/icons-vue'  // 添加这行
import {
  formatFileSize,
  DocumentStatusText,
  FileTypeText,
} from '@/api/v2/document_manager/index'
import { getToken } from '@/utils/auth'  // 添加这行


const router = useRouter()
// 查看PDF文档
const viewPdfDocument = async () => {
  if (!props.document?.id) return

  try {
    const response = await fetch(`${API_BASE_URL}/v2/document_manager/documents/${props.document.id}/stream`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`  // 手动添加Token
      }
    })

    if (!response.ok) {
      throw new Error('获取PDF失败')
    }

    // 创建Blob URL并在新窗口打开
    const blob = await response.blob()
    const pdfUrl = window.URL.createObjectURL(blob)
    window.open(pdfUrl, '_blank')

    // 清理内存
    setTimeout(() => {
      window.URL.revokeObjectURL(pdfUrl)
    }, 1000)

  } catch (error) {
    console.error('查看PDF失败:', error)
    ElMessage.error('查看PDF失败')
  }
}

// 下载PDF文档
const downloadPdfDocument = async () => {
  if (!props.document?.id) return

  try {
    const response = await fetch(`${API_BASE_URL}/v2/document_manager/documents/${props.document.id}/download`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`  // 手动添加Token
      }
    })

    if (!response.ok) {
      throw new Error('下载PDF失败')
    }

    // 获取文件名
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = props.document.title + '.pdf'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*?=['"]?([^'";]+)['"]?/)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1])
      }
    }

    // 下载文件
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)

  } catch (error) {
    console.error('下载PDF失败:', error)
    ElMessage.error('下载PDF失败')
  }
}
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  document: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

// 对话框显示状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 获取文件类型文本
const getFileTypeText = (fileType) => {
  return FileTypeText[fileType] || fileType
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    draft: '',
    published: 'success',
    review_failed: 'danger'
  }
  return typeMap[status] || ''
}

// 获取状态文本
const getStatusText = (status) => {
  return DocumentStatusText[status] || status
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取内容预览（前500字符）
const getPreviewContent = (content) => {
  if (!content) return ''
  return content.length > 500
    ? content.substring(0, 500) + '...'
    : content
}

// 编辑文档
const editDocument = () => {
  router.push({
    path: '/document-editor',
    query: { id: props.document.id }
  })
  handleClose()
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.document-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #d0d7de;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.info-label {
  color: #656d76;
  min-width: 90px;
}

.info-value {
  color: #24292f;
  font-weight: 500;
}

.summary-text {
  font-size: 14px;
  color: #24292f;
  line-height: 1.6;
  margin: 0;
  padding: 12px;
  background: #f6f8fa;
  border-radius: 6px;
}

.content-preview {
  font-size: 14px;
  color: #24292f;
  line-height: 1.8;
  padding: 16px;
  background: #f6f8fa;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 滚动条样式 */
.document-detail::-webkit-scrollbar,
.content-preview::-webkit-scrollbar {
  width: 6px;
}

.document-detail::-webkit-scrollbar-thumb,
.content-preview::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.document-detail::-webkit-scrollbar-thumb:hover,
.content-preview::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}
</style>
