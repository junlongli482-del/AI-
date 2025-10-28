<template>
  <div class="folder-tree-container">
    <!-- 头部操作区 -->
    <div class="tree-header">
      <h3 class="tree-title">📁 文件夹</h3>
      <el-button
        type="primary"
        size="small"
        @click="showCreateDialog(null)"
        :icon="Plus"
      >
        新建
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 文件夹树 -->
    <div v-else class="tree-content">
      <!-- 根目录 -->
      <div
        class="tree-node root-node"
        :class="{ active: selectedFolderId === null }"
        @click="selectFolder(null)"
      >
        <div class="node-content">
          <span class="node-icon">🏠</span>
          <span class="node-label">全部文档</span>
          <span class="node-count">({{ rootDocCount }})</span>
        </div>
      </div>

      <!-- 递归渲染文件夹树 -->
      <div class="tree-list">
        <FolderNode
          v-for="folder in folderTree"
          :key="folder.id"
          :folder="folder"
          :selected-id="selectedFolderId"
          @select="selectFolder"
          @create="showCreateDialog"
          @delete="handleDelete"
        />
      </div>

      <!-- 空状态 -->
      <div v-if="folderTree.length === 0" class="empty-state">
        <el-empty
          description="暂无文件夹"
          :image-size="80"
        >
          <el-button type="primary" size="small" @click="showCreateDialog(null)">
            创建第一个文件夹
          </el-button>
        </el-empty>
      </div>
    </div>

    <!-- 创建文件夹对话框 -->
    <CreateFolder
      v-model="createDialogVisible"
      :parent-folder="currentParentFolder"
      @success="handleCreateSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Loading } from '@element-plus/icons-vue'
import { getFolderTree, deleteFolder } from '@/api/v2/document_manager/folder'
import CreateFolder from './CreateFolder.vue'
import FolderNode from './FolderNode.vue'

// 响应式数据
const loading = ref(false)
const folderTree = ref([])
const selectedFolderId = ref(null)
const createDialogVisible = ref(false)
const currentParentFolder = ref(null)
const rootDocCount = ref(0)

// 事件定义
const emit = defineEmits(['folder-select', 'tree-update'])

// 加载文件夹树
const loadFolderTree = async () => {
  loading.value = true
  try {
    const data = await getFolderTree()
    folderTree.value = data

    // 计算根目录文档数
    rootDocCount.value = calculateRootDocCount(data)

    emit('tree-update', data)
  } catch (error) {
    ElMessage.error('加载文件夹失败')
    console.error('加载文件夹树失败:', error)
  } finally {
    loading.value = false
  }
}

// 计算根目录文档数（递归统计所有文件夹的文档数）
const calculateRootDocCount = (folders) => {
  let count = 0
  folders.forEach(folder => {
    count += folder.document_count || 0
    if (folder.children && folder.children.length > 0) {
      count += calculateRootDocCount(folder.children)
    }
  })
  return count
}

// 选择文件夹
const selectFolder = (folderId) => {
  selectedFolderId.value = folderId
  emit('folder-select', folderId)
}

// 显示创建对话框
const showCreateDialog = (parentFolder) => {
  currentParentFolder.value = parentFolder
  createDialogVisible.value = true
}

// 创建成功回调
const handleCreateSuccess = () => {
  loadFolderTree()
  ElMessage.success('文件夹创建成功')
}

// 删除文件夹
const handleDelete = async (folder) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件夹"${folder.name}"吗？只能删除空文件夹。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteFolder(folder.id)
    ElMessage.success('文件夹删除成功')

    // 如果删除的是当前选中的文件夹，切换到根目录
    if (selectedFolderId.value === folder.id) {
      selectFolder(null)
    }

    loadFolderTree()
  } catch (error) {
    if (error !== 'cancel') {
      // ElMessage.error 已在 request.js 中处理
      console.error('删除文件夹失败:', error)
    }
  }
}

// 暴露刷新方法
defineExpose({
  refresh: loadFolderTree
})

// 组件挂载时加载数据
onMounted(() => {
  loadFolderTree()
})
</script>

<style scoped>
.folder-tree-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #d0d7de;
}

.tree-header {
  padding: 16px;
  border-bottom: 1px solid #d0d7de;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-title {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
  margin: 0;
}

.loading-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #656d76;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tree-node {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 4px;
}

.tree-node:hover {
  background: #f6f8fa;
}

.tree-node.active {
  background: #e8f4ff;
  color: #007AFF;
}

.root-node {
  font-weight: 500;
  margin-bottom: 8px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-icon {
  font-size: 16px;
}

.node-label {
  flex: 1;
  font-size: 14px;
}

.node-count {
  font-size: 12px;
  color: #656d76;
}

.tree-list {
  margin-top: 8px;
}

.empty-state {
  padding: 32px 16px;
}

/* 滚动条样式 */
.tree-content::-webkit-scrollbar {
  width: 6px;
}

.tree-content::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.tree-content::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}
</style>
