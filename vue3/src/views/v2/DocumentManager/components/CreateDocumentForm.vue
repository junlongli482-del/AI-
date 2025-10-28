<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建文档"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      label-position="top"
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

      <!-- 文档摘要 -->
      <el-form-item label="文档摘要（可选）" prop="summary">
        <el-input
          v-model="formData.summary"
          type="textarea"
          placeholder="请输入文档摘要"
          :rows="3"
          maxlength="500"
          show-word-limit
          clearable
        />
      </el-form-item>

      <!-- 所属文件夹 -->
      <el-form-item label="所属文件夹" prop="folder_id">
        <el-tree-select
          v-model="formData.folder_id"
          :data="folderTreeData"
          placeholder="请选择文件夹"
          :props="treeProps"
          check-strictly
          :render-after-expand="false"
          clearable
          style="width: 100%"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          创建文档
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createDocumentFromUpload, extractTitleFromFilename } from '@/api/v2/file_upload/index'
import { getFolderTree } from '@/api/v2/document_manager/folder'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  uploadResult: {
    type: Object,
    default: null
  }
})

// 事件定义
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)
const folderTreeData = ref([])

// 表单数据
const formData = reactive({
  title: '',
  summary: '',
  folder_id: null
})

// 表单验证规则
const formRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  summary: [
    { max: 500, message: '摘要不能超过 500 个字符', trigger: 'blur' }
  ]
}

// 树形选择器配置
const treeProps = {
  label: 'name',
  value: 'id',
  children: 'children'
}

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    initForm()
    loadFolderTree()
  }
})

// 监听 dialogVisible 变化
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
  }
})

// 初始化表单
const initForm = () => {
  if (props.uploadResult) {
    // 从文件名提取标题（去掉扩展名）
    formData.title = extractTitleFromFilename(props.uploadResult.file_info.original_filename)
    formData.summary = ''
    formData.folder_id = null
  }
}

// 加载文件夹树
const loadFolderTree = async () => {
  try {
    const data = await getFolderTree()

    // 添加"全部文档（根目录）"选项
    folderTreeData.value = [
      {
        id: null,
        name: '全部文档（根目录）',
        children: data
      }
    ]
  } catch (error) {
    console.error('加载文件夹树失败:', error)
    ElMessage.error('加载文件夹列表失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    // 验证表单
    await formRef.value.validate()

    loading.value = true

    // 调用创建文档接口
    const result = await createDocumentFromUpload({
      upload_id: props.uploadResult.upload_id,
      title: formData.title,
      summary: formData.summary || undefined,
      folder_id: formData.folder_id || undefined
    })

    ElMessage.success('文档创建成功')
    emit('success', result)
    handleClose()
  } catch (error) {
    if (error.errors) {
      // 表单验证失败
      return
    }
    console.error('创建文档失败:', error)
    ElMessage.error(error.message || '创建文档失败')
  } finally {
    loading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  formRef.value?.resetFields()
  dialogVisible.value = false
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #24292f;
}

:deep(.el-input__inner) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
}

:deep(.el-tree-select) {
  border-radius: 6px;
}
</style>
