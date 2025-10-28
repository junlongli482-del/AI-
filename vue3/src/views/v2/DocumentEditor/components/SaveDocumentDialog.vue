<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
    destroy-on-close
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="80px"
      @submit.prevent="handleSave"
    >
      <!-- 文档标题 -->
      <el-form-item label="文档标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="请输入文档标题"
          maxlength="200"
          show-word-limit
          clearable
        />
      </el-form-item>

      <!-- 文件夹选择 -->
      <el-form-item label="保存位置" prop="folder_id">
        <el-tree-select
          v-model="formData.folder_id"
          :data="folderTreeData"
          :props="treeProps"
          :placeholder="folderPlaceholder"
          clearable
          check-strictly
          :render-after-expand="false"
          style="width: 100%"
        />
        <!-- 添加提示信息 -->
        <div class="folder-hint">
          <el-text size="small" type="info">
            {{ folderHint }}
          </el-text>
        </div>
      </el-form-item>

      <!-- 文档摘要 -->
      <el-form-item label="文档摘要">
        <el-input
          v-model="formData.summary"
          type="textarea"
          :rows="3"
          placeholder="请输入文档摘要（可选）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="saving"
          @click="handleSave"
        >
          {{ saveButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { saveAsDocument, generateDefaultTitle } from '@/api/v2/md_editor/index'
import { getFolderTree } from '@/api/v2/document_manager/folder'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  sessionData: {
    type: Object,
    default: null
  },
  defaultFolderId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'document-saved'])

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref(null)
const saving = ref(false)
const folderTreeData = ref([])

// 表单数据
const formData = ref({
  title: '',
  folder_id: null,
  summary: ''
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
  ]
}

// 树形选择器配置
const treeProps = {
  value: 'id',
  label: 'name',
  children: 'children'
}

// 计算属性
const isEditMode = computed(() => {
  return props.sessionData?.session_type === 'edit_document'
})

const dialogTitle = computed(() => {
  // 统一显示"保存文档"
  return '保存文档'
})

const saveButtonText = computed(() => {
  // 统一显示"保存文档"
  return '保存文档'
})

// 文件夹提示
const folderPlaceholder = computed(() => {
  return isEditMode.value
    ? '选择文件夹（默认原文件夹）'
    : '选择文件夹（默认根目录）'
})

const folderHint = computed(() => {
  return isEditMode.value
    ? '💡 不选择文件夹将保存到原文档所在的文件夹'
    : '💡 不选择文件夹将保存到根目录'
})

// 监听对话框打开
watch(visible, async (newVisible) => {
  if (newVisible) {
    await initializeDialog()
  } else {
    resetForm()
  }
})

// 初始化对话框
// 初始化对话框
const initializeDialog = async () => {
  try {
    // 加载文件夹树
    await loadFolderTree()

    // 初始化表单数据
    if (props.sessionData) {
      // 编辑模式：保持原标题，新建模式：生成新标题
      if (isEditMode.value) {
        formData.value.title = props.sessionData.title || '未命名文档'
      } else {
        formData.value.title = generateDefaultTitle(props.sessionData.content || '')
      }

      // 根据模式设置默认文件夹
      if (isEditMode.value) {
        // 编辑模式：默认使用原文档的文件夹
        formData.value.folder_id = props.sessionData.folder_id || null
      } else {
        // 新建模式：默认使用指定文件夹或根目录
        formData.value.folder_id = props.defaultFolderId || null
      }

      // 编辑模式：保持原摘要，新建模式：清空摘要
      if (isEditMode.value) {
        formData.value.summary = props.sessionData.summary || ''
      } else {
        formData.value.summary = ''
      }
    }
  } catch (error) {
    console.error('初始化对话框失败:', error)
    ElMessage.error('初始化失败')
  }
}

// 加载文件夹树
const loadFolderTree = async () => {
  try {
    const response = await getFolderTree()

    // 添加根目录选项
    folderTreeData.value = [
      {
        id: null,
        name: '根目录',
        children: response || []
      }
    ]
  } catch (error) {
    console.error('加载文件夹树失败:', error)
    folderTreeData.value = [
      {
        id: null,
        name: '根目录',
        children: []
      }
    ]
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  formData.value = {
    title: '',
    folder_id: null,
    summary: ''
  }
  saving.value = false
}

// 保存文档
const handleSave = async () => {
  if (!formRef.value || !props.sessionData) return

  try {
    // 表单验证
    await formRef.value.validate()

    saving.value = true

    // 调用保存接口
    const response = await saveAsDocument(props.sessionData.id, {
      title: formData.value.title.trim(),
      folder_id: formData.value.folder_id,
      summary: formData.value.summary?.trim() || undefined
    })

    // 通知父组件保存成功
    emit('document-saved', {
      document_id: response.document_id,
      document_title: response.document_title
    })

    // 关闭对话框
    visible.value = false

  } catch (error) {
    console.error('保存文档失败:', error)

    if (error.errors) {
      // 表单验证错误
      const firstError = Object.values(error.errors)[0]
      ElMessage.error(Array.isArray(firstError) ? firstError[0] : firstError)
    } else {
      ElMessage.error(error.message || '保存失败')
    }
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 组件挂载时加载文件夹树（预加载）
onMounted(() => {
  loadFolderTree()
})
</script>

<style scoped>
.folder-hint {
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #24292f;
}

:deep(.el-input__wrapper) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
  font-family: inherit;
}

:deep(.el-tree-select) {
  border-radius: 6px;
}

/* 树形选择器样式 */
:deep(.el-tree-select__popper .el-tree-node__content) {
  padding: 8px 12px;
  border-radius: 4px;
  margin: 2px 4px;
}

:deep(.el-tree-select__popper .el-tree-node__content:hover) {
  background: #f6f8fa;
}

:deep(.el-tree-select__popper .el-tree-node.is-current > .el-tree-node__content) {
  background: #f0f8ff;
  color: #007AFF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95vw;
    margin: 5vh auto;
  }

  :deep(.el-form-item__label) {
    width: 70px !important;
  }
}
</style>
