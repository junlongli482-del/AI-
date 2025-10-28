<template>
  <el-dialog
    v-model="dialogVisible"
    title="上传文件"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 上传区域 -->
    <div v-if="!isUploading && fileList.length === 0" class="upload-section">
      <UploadArea @files-selected="handleFilesSelected" />
    </div>

    <!-- 文件列表和进度 -->
    <div v-if="fileList.length > 0" class="progress-section">
      <div class="section-header">
        <h3 class="section-title">
          已选择文件 ({{ fileList.length }})
          <span v-if="uploadStats.total > 0" class="upload-stats">
            - 成功: {{ uploadStats.success }} / 失败: {{ uploadStats.failed }}
          </span>
        </h3>
        <el-button
          v-if="!isUploading && hasValidatedFiles"
          text
          @click="clearAllFiles"
        >
          清空列表
        </el-button>
      </div>

      <UploadProgress
        :file-list="fileList"
        @remove-file="removeFile"
      />
    </div>

    <!-- 底部操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">
          {{ isUploading ? '后台上传' : '取消' }}
        </el-button>
        <el-button
          v-if="!isUploading && hasValidatedFiles"
          type="primary"
          @click="startUpload"
        >
          开始上传 ({{ validatedFilesCount }})
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 创建文档表单 -->
  <CreateDocumentForm
    v-model:visible="showCreateForm"
    :upload-result="currentUploadResult"
    @success="handleDocumentCreated"
  />
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import UploadArea from './UploadArea.vue'
import UploadProgress from './UploadProgress.vue'
import CreateDocumentForm from './CreateDocumentForm.vue'
import { validateFile, uploadFile } from '@/api/v2/file_upload/index'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
})

// 事件定义
const emit = defineEmits(['update:visible', 'upload-success'])

// 响应式数据
const dialogVisible = ref(false)
const fileList = ref([])
const isUploading = ref(false)
const showCreateForm = ref(false)
const currentUploadResult = ref(null)
const fileIdCounter = ref(0)

// 上传统计
const uploadStats = reactive({
  total: 0,
  success: 0,
  failed: 0
})

// 计算属性
const hasValidatedFiles = computed(() => {
  return fileList.value.some(item => item.status === 'validated')
})

const validatedFilesCount = computed(() => {
  return fileList.value.filter(item => item.status === 'validated').length
})

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    resetUpload()
  }
})

// 监听 dialogVisible 变化
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
  }
})

// 重置上传状态
const resetUpload = () => {
  fileList.value = []
  isUploading.value = false
  uploadStats.total = 0
  uploadStats.success = 0
  uploadStats.failed = 0
}

// 处理文件选择
const handleFilesSelected = async (files) => {
  // ⭐ 修改：使用 reactive 包装每个文件对象
  const newFiles = files.map(file => reactive({
    id: ++fileIdCounter.value,
    file,
    status: 'validating', // validating, validated, uploading, success, error
    progress: 0,
    errorMessage: '',
    uploadResult: null
  }))

  fileList.value.push(...newFiles)

  // 验证每个文件
  for (const item of newFiles) {
    await validateSingleFile(item)
  }
}

// 验证单个文件
const validateSingleFile = async (item) => {
  console.log('🔍 开始验证文件:', item.file.name)

  try {
    console.log('📤 调用验证接口...')
    const result = await validateFile(item.file)

    console.log('✅ 验证接口返回:', result)

    if (result.is_valid) {
      item.status = 'validated'
      console.log('✅ 文件验证通过，状态已更新为:', item.status)
    } else {
      item.status = 'error'
      item.errorMessage = result.error_message || '验证失败'
      console.log('❌ 文件验证失败:', item.errorMessage)
    }
  } catch (error) {
    console.error('❌ 文件验证异常:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response,
      request: error.request
    })

    item.status = 'error'
    item.errorMessage = error.message || '验证失败'
  }
}

// 开始上传
const startUpload = async () => {
  const validatedFiles = fileList.value.filter(item => item.status === 'validated')

  if (validatedFiles.length === 0) {
    ElMessage.warning('没有可上传的文件')
    return
  }

  isUploading.value = true
  uploadStats.total = validatedFiles.length
  uploadStats.success = 0
  uploadStats.failed = 0

  // 循环上传每个文件
  for (const item of validatedFiles) {
    await uploadSingleFile(item)
  }

  isUploading.value = false

  // 显示上传结果
  if (uploadStats.success > 0) {
    ElMessage.success(`成功上传 ${uploadStats.success} 个文件`)
  }
  if (uploadStats.failed > 0) {
    ElMessage.error(`${uploadStats.failed} 个文件上传失败`)
  }
}

// 上传单个文件
const uploadSingleFile = async (item) => {
  item.status = 'uploading'
  item.progress = 0

  try {
    const result = await uploadFile(item.file, (progress) => {
      item.progress = progress
    })

    if (result.success) {
      item.status = 'success'
      item.uploadResult = result
      uploadStats.success++

      // 上传成功后弹出创建文档表单
      currentUploadResult.value = result
      showCreateForm.value = true

      // 等待用户创建文档或关闭表单
      await new Promise(resolve => {
        const unwatch = watch(showCreateForm, (newVal) => {
          if (!newVal) {
            unwatch()
            resolve()
          }
        })
      })
    } else {
      item.status = 'error'
      item.errorMessage = result.message || '上传失败'
      uploadStats.failed++
    }
  } catch (error) {
    console.error('文件上传失败:', error)
    item.status = 'error'
    item.errorMessage = error.message || '上传失败'
    uploadStats.failed++
  }
}

// 移除文件
const removeFile = (fileId) => {
  const index = fileList.value.findIndex(item => item.id === fileId)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 清空所有文件
const clearAllFiles = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有文件吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    fileList.value = []
  } catch {
    // 用户取消
  }
}

// 处理文档创建成功
const handleDocumentCreated = (result) => {
  emit('upload-success', result)
}

// 关闭对话框
const handleClose = () => {
  if (isUploading.value) {
    ElMessage.info('文件正在后台上传')
  }
  dialogVisible.value = false
}
</script>

<style scoped>
.upload-section {
  margin-bottom: 24px;
}

.progress-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #24292f;
  margin: 0;
}

.upload-stats {
  font-size: 14px;
  font-weight: normal;
  color: #656d76;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
