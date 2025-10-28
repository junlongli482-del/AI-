<template>
  <div class="document-editor">
    <!-- 全局导航 -->
    <AppHeader />

    <!-- 编辑器容器 -->
    <div class="editor-container">
      <!-- 工具栏 -->
      <EditorToolbar
        :view-mode="viewMode"
        :session-data="sessionData"
        :has-unsaved-changes="hasUnsavedChanges"
        :is-saving="isSaving"
        :can-undo="canUndo"
        :can-redo="canRedo"
        @view-change="handleViewChange"
        @save-as="handleSaveAs"
        @ai-optimize="handleAIOptimize"
        @undo="handleUndo"
        @redo="handleRedo"
      />

      <!-- 编辑器主体 -->
      <div class="editor-main">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载编辑器...</span>
        </div>

        <!-- 编辑器内容 -->
        <div v-else class="editor-content">
          <!-- 模式1：编辑全屏 -->
          <div v-if="viewMode === 'edit'" class="editor-layout edit-only">
            <MarkdownEditor
              ref="editorRef"
              v-model:content="content"
              :session-id="sessionData?.id"
              @content-change="handleContentChange"
              @ready="handleEditorReady"
            />
          </div>

          <!-- 模式2：分屏模式 -->
          <div v-else-if="viewMode === 'split'" class="editor-layout split-view">
            <div class="editor-panel">
              <MarkdownEditor
                ref="editorRef"
                v-model:content="content"
                :session-id="sessionData?.id"
                @content-change="handleContentChange"
                @ready="handleEditorReady"
              />
            </div>
            <div class="preview-panel">
              <PreviewPanel :content="content" />
            </div>
          </div>

          <!-- 模式3：预览全屏 -->
          <div v-else-if="viewMode === 'preview'" class="editor-layout preview-only">
            <PreviewPanel :content="content" />
          </div>
        </div>
      </div>
    </div>

    <!-- AI优化对话框 -->
    <AIOptimizeDialog
      v-model="optimizeDialogVisible"
      :session-id="sessionData?.id"
      :optimize-data="optimizeData"
    />

    <!-- 保存文档对话框 -->
    <SaveDocumentDialog
      v-model="saveDialogVisible"
      :session-data="sessionData"
      :default-folder-id="defaultFolderId"
      @document-saved="handleDocumentSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import EditorToolbar from './components/EditorToolbar.vue'
import MarkdownEditor from './components/MarkdownEditor.vue'
import PreviewPanel from './components/PreviewPanel.vue'
import AIOptimizeDialog from './components/AIOptimizeDialog.vue'
import SaveDocumentDialog from './components/SaveDocumentDialog.vue'
import {
  createSession,
  updateSession,
  generateDefaultTitle
} from '@/api/v2/md_editor/index'

const route = useRoute()
const router = useRouter()

// ==================== 响应式数据 ====================

const loading = ref(true)
const viewMode = ref('edit') // 'edit' | 'split' | 'preview'
const content = ref('')
const sessionData = ref(null)
const editorRef = ref(null)
const hasUnsavedChanges = ref(false)
const isSaving = ref(false)
const lastSavedContent = ref('')

// 撤销/重做状态
const canUndo = ref(false)
const canRedo = ref(false)

// 对话框状态
const optimizeDialogVisible = ref(false)
const saveDialogVisible = ref(false)
const optimizeData = ref(null)

// 路由参数
const documentId = ref(null)
const defaultFolderId = ref(null)

// ==================== 初始化逻辑 ====================

onMounted(async () => {
  try {
    // 解析路由参数
    documentId.value = route.query.id ? parseInt(route.query.id) : null
    defaultFolderId.value = route.query.folder_id ? parseInt(route.query.folder_id) : null

    await initializeEditor()
    setupKeyboardShortcuts()
    setupBeforeUnload()
  } catch (error) {
    console.error('编辑器初始化失败:', error)
    ElMessage.error('编辑器初始化失败')
    router.push('/document-manager')
  }
})

onUnmounted(() => {
  cleanupBeforeUnload()
  document.removeEventListener('keydown', handleKeydown)
})

// ==================== 编辑器初始化 ====================

const initializeEditor = async () => {
  loading.value = true

  try {
    if (documentId.value) {
      // 编辑现有文档
      await initializeEditSession()
    } else {
      // 新建文档
      await initializeNewSession()
    }
  } finally {
    loading.value = false
  }
}

const initializeNewSession = async () => {
  const sessionResponse = await createSession({
    session_type: 'new_document',
    title: '未命名文档',
    content: ''
  })

  sessionData.value = sessionResponse
  content.value = ''
  lastSavedContent.value = ''
  hasUnsavedChanges.value = false
}

const initializeEditSession = async () => {
  const sessionResponse = await createSession({
    document_id: documentId.value,
    session_type: 'edit_document'
  })

  sessionData.value = sessionResponse
  content.value = sessionResponse.content || ''
  lastSavedContent.value = content.value
  hasUnsavedChanges.value = false
}

// ==================== 视图模式切换 ====================

const handleViewChange = (mode) => {
  viewMode.value = mode
}

// ==================== 内容变化处理 ====================

const handleContentChange = (newContent) => {
  content.value = newContent
  hasUnsavedChanges.value = newContent !== lastSavedContent.value

  // 更新撤销/重做状态
  updateUndoRedoState()
}

const handleEditorReady = () => {
  // 编辑器准备就绪
  console.log('编辑器准备就绪')
  // 初始化撤销/重做状态
  updateUndoRedoState()
}

// ==================== 撤销/重做功能 ====================

const handleUndo = () => {
  if (editorRef.value) {
    editorRef.value.undo()
    updateUndoRedoState()
  }
}

const handleRedo = () => {
  if (editorRef.value) {
    editorRef.value.redo()
    updateUndoRedoState()
  }
}

const updateUndoRedoState = () => {
  if (editorRef.value) {
    canUndo.value = editorRef.value.canUndo()
    canRedo.value = editorRef.value.canRedo()
  }
}

// ==================== 统一保存功能 ====================

// 保存功能（新建和编辑都用这个）
// 保存功能（新建和编辑都用这个）
const handleSaveAs = async () => {
  if (!sessionData.value) return

  if (!content.value.trim()) {
    ElMessage.warning('请先输入文档内容')
    return
  }

  isSaving.value = true

  try {
    // 第一步：先更新会话内容（重要！）
    await updateSession(sessionData.value.id, {
      content: content.value,
      title: sessionData.value.title || generateDefaultTitle(content.value)
    })

    // 更新本地会话数据
    sessionData.value.content = content.value
    if (!sessionData.value.title || sessionData.value.title === '未命名文档') {
      sessionData.value.title = generateDefaultTitle(content.value)
    }

    // 第二步：弹出对话框选择保存位置
    saveDialogVisible.value = true

  } catch (error) {
    console.error('保存会话失败:', error)
    ElMessage.error('保存失败')
  } finally {
    isSaving.value = false
  }
}
const handleDocumentSaved = (result) => {
  ElMessage.success('文档保存成功')

  // 更新本地状态
  lastSavedContent.value = content.value
  hasUnsavedChanges.value = false

  // 如果是新建文档，转换为编辑模式
  if (sessionData.value.session_type === 'new_document') {
    sessionData.value.document_id = result.document_id
    sessionData.value.session_type = 'edit_document'
  }

  // 询问是否查看文档
  ElMessageBox.confirm(
    '文档保存成功！是否前往查看？',
    '保存成功',
    {
      confirmButtonText: '查看文档',
      cancelButtonText: '继续编辑',
      type: 'success'
    }
  ).then(() => {
    router.push('/document-manager')
  }).catch(() => {
    // 继续编辑，状态已经更新
  })
}

// ==================== AI优化功能 ====================

const handleAIOptimize = () => {
  if (!sessionData.value) return

  // 获取选中内容或全部内容
  const selectedData = editorRef.value?.getSelectedText()
  if (!selectedData) {
    ElMessage.warning('无法获取编辑器内容')
    return
  }

  optimizeData.value = selectedData
  optimizeDialogVisible.value = true
}


// ==================== 快捷键 ====================

const setupKeyboardShortcuts = () => {
  document.addEventListener('keydown', handleKeydown)
}

const handleKeydown = (e) => {
  // 完全禁用Ctrl+S，避免浏览器默认行为和用户误解
  if (e.ctrlKey && e.key === 's') {
    e.preventDefault()
    e.stopPropagation()
    return false
  }

  // Ctrl+Z 撤销
  if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    handleUndo()
  }

  // Ctrl+Y 重做
  if (e.ctrlKey && e.key === 'y') {
    e.preventDefault()
    handleRedo()
  }
}

// ==================== 页面离开提示 ====================

const setupBeforeUnload = () => {
  window.addEventListener('beforeunload', handleBeforeUnload)
}

const cleanupBeforeUnload = () => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
}

const handleBeforeUnload = (e) => {
  if (hasUnsavedChanges.value) {
    e.preventDefault()
    e.returnValue = '您有未保存的内容，确定离开吗？'
  }
}

// ==================== 路由守卫 ====================

// 监听路由变化
watch(() => route.path, (newPath, oldPath) => {
  if (oldPath === '/document-editor' && hasUnsavedChanges.value) {
    // 如果是从编辑器页面离开且有未保存内容，在路由守卫中处理
  }
})
</script>

<style scoped>
.document-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.editor-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 编辑器布局模式 */
.editor-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 编辑全屏模式 */
.edit-only {
  flex-direction: column;
}

/* 分屏模式 */
.split-view {
  flex-direction: row;
}

.editor-panel {
  flex: 1;
  border-right: 1px solid #d0d7de;
  overflow: hidden;
}

.preview-panel {
  flex: 1;
  overflow: hidden;
}

/* 预览全屏模式 */
.preview-only {
  flex-direction: column;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .split-view {
    flex-direction: column;
  }

  .editor-panel {
    border-right: none;
    border-bottom: 1px solid #d0d7de;
  }
}
</style>
