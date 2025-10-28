<template>
  <div class="upload-history-container">
    <!-- 头部：筛选和统计 -->
    <div class="history-header">
      <div class="filter-bar">
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          style="width: 150px"
          @change="loadHistory"
        >
          <el-option label="全部" value="" />
          <el-option label="已验证" value="validated" />
          <el-option label="失败" value="failed" />
        </el-select>
      </div>
      <div class="stats-info">
        <span class="stat-text">总上传：{{ uploadStats.total_uploads || 0 }}</span>
        <span class="stat-text">总大小：{{ uploadStats.total_size_mb?.toFixed(2) || 0 }} MB</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 上传历史列表 -->
    <div v-else-if="uploadList.length > 0" class="upload-list">
      <div
        v-for="upload in uploadList"
        :key="upload.id"
        class="upload-item"
        :class="{ 'is-failed': upload.status === 'failed' }"
      >
        <div class="upload-info">
          <div class="upload-header">
            <span class="file-icon">{{ getFileIcon(upload.file_type) }}</span>
            <h4 class="file-name">{{ upload.original_filename }}</h4>
            <el-tag
              :type="getStatusTagType(upload.status)"
              size="small"
            >
              {{ getStatusText(upload.status) }}
            </el-tag>
          </div>

          <div class="upload-meta">
            <span class="meta-item">
              📏 {{ formatFileSize(upload.file_size) }}
            </span>
            <span class="meta-item">
              🕐 {{ formatDate(upload.created_at) }}
            </span>
            <span v-if="upload.validation_message" class="meta-item validation-msg">
              {{ upload.validation_message }}
            </span>
          </div>
        </div>

        <div class="upload-actions">
          <el-button
            v-if="upload.status === 'validated'"
            type="primary"
            size="small"
            @click="createDocument(upload)"
          >
            创建文档
          </el-button>
          <el-button
            type="text"
            size="small"
            class="delete-btn"
            @click="deleteUpload(upload)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="暂无上传记录" />
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 创建文档表单 -->
    <CreateDocumentForm
      v-model:visible="showCreateForm"
      :upload-result="currentUploadResult"
      @success="handleDocumentCreated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import {
  getUploadHistory,
  deleteUploadRecord,
  getUploadStats,
  formatFileSize,
  UploadStatusText
} from '@/api/v2/file_upload/index'
import CreateDocumentForm from './CreateDocumentForm.vue'

// 事件定义
const emit = defineEmits(['create-document'])

// 响应式数据
const loading = ref(false)
const uploadList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const statusFilter = ref('')
const uploadStats = ref({})
const showCreateForm = ref(false)
const currentUploadResult = ref(null)

// 加载上传历史
const loadHistory = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (statusFilter.value) {
      params.status_filter = statusFilter.value
    }

    const data = await getUploadHistory(params)
    uploadList.value = data.files
    total.value = data.total
  } catch (error) {
    console.error('加载上传历史失败:', error)
    ElMessage.error('加载上传历史失败')
  } finally {
    loading.value = false
  }
}

// 加载统计信息
const loadStats = async () => {
  try {
    const data = await getUploadStats()
    uploadStats.value = data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

// 分页处理
const handlePageChange = () => {
  loadHistory()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadHistory()
}

// 创建文档
const createDocument = (upload) => {
  currentUploadResult.value = {
    upload_id: upload.id,
    file_info: {
      original_filename: upload.original_filename,
      file_size: upload.file_size,
      file_type: upload.file_type
    }
  }
  showCreateForm.value = true
}

// 删除上传记录
const deleteUpload = async (upload) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除上传记录"${upload.original_filename}"吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteUploadRecord(upload.id)
    ElMessage.success('删除成功')
    loadHistory()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 处理文档创建成功
const handleDocumentCreated = () => {
  ElMessage.success('文档创建成功')
  loadHistory()
  emit('create-document')
}

// 获取文件图标
const getFileIcon = (fileType) => {
  return fileType === 'pdf' ? '📕' : '📄'
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    validated: 'success',
    failed: 'danger',
    uploaded: 'info'
  }
  return typeMap[status] || ''
}

// 获取状态文本
const getStatusText = (status) => {
  return UploadStatusText[status] || status
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时加载数据
onMounted(() => {
  loadHistory()
  loadStats()
})
</script>

<!-- 接上面的代码，从 <style scoped> 开始 -->

<style scoped>
.upload-history-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  overflow: hidden; /* 防止整体滚动 */
}

.history-header {
  padding: 16px 24px;
  border-bottom: 1px solid #d0d7de;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.filter-bar {
  display: flex;
  gap: 12px;
}

.stats-info {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #656d76;
}

.stat-text {
  font-weight: 500;
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #656d76;
  overflow: hidden;
}

.upload-list {
  flex: 1;
  overflow-y: auto; /* 允许列表滚动 */
  overflow-x: hidden;
  padding: 16px 24px;
}

.upload-item {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-item:hover {
  border-color: #007AFF;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.1);
}

.upload-item.is-failed {
  border-color: #ff4d4f;
  background: #fff2f0;
}

.upload-info {
  flex: 1;
  min-width: 0; /* 允许内容收缩 */
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.file-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #656d76;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.validation-msg {
  color: #ff4d4f;
  font-weight: 500;
}

.upload-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.delete-btn {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f56c6c;
  background: #fef0f0;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  overflow: hidden;
}

.pagination-container {
  padding: 16px 24px;
  border-top: 1px solid #d0d7de;
  display: flex;
  justify-content: center;
  flex-shrink: 0; /* 防止分页被压缩 */
}

/* 滚动条样式 */
.upload-list::-webkit-scrollbar {
  width: 6px;
}

.upload-list::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.upload-list::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
  }

  .stats-info {
    width: 100%;
    justify-content: space-between;
  }

  .upload-list {
    padding: 12px 16px;
  }

  .upload-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .upload-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
