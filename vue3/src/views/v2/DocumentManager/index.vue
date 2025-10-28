<template>
  <div class="document-manager-page">
    <!-- 全局导航 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <div class="page-content">
      <div class="content-wrapper">
        <!-- 左侧：文件夹树 -->
        <aside class="sidebar">
          <FolderTree
            ref="folderTreeRef"
            @folder-select="handleFolderSelect"
            @tree-update="handleTreeUpdate"
          />
        </aside>

        <!-- 右侧：文档列表 -->
        <main class="main-content">
          <DocumentList
            ref="documentListRef"
            :folder-id="selectedFolderId"
            :stats="stats"
            @refresh-stats="loadStats"
            @open-upload="showUploadDialog"
          />
        </main>
      </div>
    </div>

    <!-- 上传文件对话框 -->
    <UploadDialog
      v-model:visible="uploadDialogVisible"
      @upload-success="handleUploadSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'
import FolderTree from './components/FolderTree.vue'
import DocumentList from './components/DocumentList.vue'
import UploadDialog from './components/UploadDialog.vue'
import { getStats } from '@/api/v2/document_manager/index'

// 响应式数据
const folderTreeRef = ref(null)
const documentListRef = ref(null)
const selectedFolderId = ref(null)
const uploadDialogVisible = ref(false)
const stats = ref({
  total_documents: 0,
  total_folders: 0,
  documents_by_status: {
    draft: 0,
    published: 0,
    review_failed: 0
  }
})

// 处理文件夹选择
const handleFolderSelect = (folderId) => {
  selectedFolderId.value = folderId
}

// 处理文件夹树更新
const handleTreeUpdate = () => {
  loadStats()
}

// 加载统计信息
const loadStats = async () => {
  try {
    const data = await getStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计信息失败:', error)
    ElMessage.error('加载统计信息失败')
  }
}

// 显示上传对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true
}

// 处理上传成功
const handleUploadSuccess = () => {
  // 刷新文档列表
  documentListRef.value?.refresh()
  // 刷新统计信息
  loadStats()
  // 刷新文件夹树（如果有新文件夹）
  folderTreeRef.value?.refresh?.()
}

// 组件挂载时加载统计
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.document-manager-page {
  min-height: 100vh;
  background: #f6f8fa;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  display: flex;
  width: 100%;
  height: calc(100vh - 64px); /* 减去导航栏高度 */
  background: #ffffff;
}

.sidebar {
  width: 280px;
  min-width: 280px;
  max-width: 400px;
  flex-shrink: 0;
  overflow-y: auto;
  background: #ffffff;
  border-right: 1px solid #d0d7de;
}

.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 重要：允许flex子项收缩 */
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
    min-width: 240px;
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
    height: auto;
  }

  .sidebar {
    width: 100%;
    max-width: 100%;
    min-width: 100%;
    max-height: 300px;
    border-right: none;
    border-bottom: 1px solid #d0d7de;
  }
}

/* 滚动条样式 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}
</style>
