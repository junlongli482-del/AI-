<template>
  <div
    class="upload-area"
    :class="{ 'is-dragover': isDragover }"
    @drop.prevent="handleDrop"
    @dragover.prevent="handleDragover"
    @dragleave.prevent="handleDragleave"
    @click="triggerFileInput"
  >
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept=".md,.pdf"
      style="display: none"
      @change="handleFileSelect"
    />

    <div class="upload-icon">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="17 8 12 3 7 8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="12" y1="3" x2="12" y2="15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <div class="upload-text">
      <p class="primary-text">拖拽文件到这里</p>
      <p class="secondary-text">或点击选择文件</p>
    </div>

    <div class="upload-hint">
      <span class="hint-item">支持 MD、PDF 格式</span>
      <span class="hint-divider">|</span>
      <span class="hint-item">MD最大20MB，PDF最大100MB</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { validateFileType, validateFileSize } from '@/api/v2/file_upload/index'

// 响应式数据
const fileInputRef = ref(null)
const isDragover = ref(false)

// 事件定义
const emit = defineEmits(['files-selected'])

// 触发文件选择
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

// 处理文件选择
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  processFiles(files)
  // 清空input，允许重复选择同一文件
  event.target.value = ''
}

// 处理拖拽放置
const handleDrop = (event) => {
  isDragover.value = false
  const files = Array.from(event.dataTransfer.files)
  processFiles(files)
}

// 处理拖拽悬停
const handleDragover = () => {
  isDragover.value = true
}

// 处理拖拽离开
const handleDragleave = () => {
  isDragover.value = false
}

// 处理文件列表
const processFiles = (files) => {
  if (!files || files.length === 0) {
    return
  }

  // 验证文件
  const validFiles = []
  const errors = []

  files.forEach(file => {
    // 验证文件类型
    const typeValidation = validateFileType(file)
    if (!typeValidation.valid) {
      errors.push(`${file.name}: ${typeValidation.message}`)
      return
    }

    // 验证文件大小
    const sizeValidation = validateFileSize(file)
    if (!sizeValidation.valid) {
      errors.push(`${file.name}: ${sizeValidation.message}`)
      return
    }

    validFiles.push(file)
  })

  // 显示错误信息
  if (errors.length > 0) {
    ElMessage.error({
      message: errors.join('\n'),
      duration: 5000,
      showClose: true
    })
  }

  // 发送有效文件
  if (validFiles.length > 0) {
    emit('files-selected', validFiles)
  }
}
</script>

<style scoped>
.upload-area {
  border: 2px dashed #d0d7de;
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f6f8fa;
}

.upload-area:hover {
  border-color: #007AFF;
  background: #ffffff;
}

.upload-area.is-dragover {
  border-color: #007AFF;
  background: #e6f2ff;
  transform: scale(1.02);
}

.upload-icon {
  color: #656d76;
  margin-bottom: 16px;
  transition: color 0.3s ease;
}

.upload-area:hover .upload-icon {
  color: #007AFF;
}

.upload-text {
  margin-bottom: 16px;
}

.primary-text {
  font-size: 18px;
  font-weight: 500;
  color: #24292f;
  margin: 0 0 8px 0;
}

.secondary-text {
  font-size: 14px;
  color: #656d76;
  margin: 0;
}

.upload-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 13px;
  color: #656d76;
}

.hint-item {
  display: inline-block;
}

.hint-divider {
  color: #d0d7de;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-area {
    padding: 32px 16px;
  }

  .upload-icon svg {
    width: 48px;
    height: 48px;
  }

  .primary-text {
    font-size: 16px;
  }

  .upload-hint {
    flex-direction: column;
    gap: 4px;
  }

  .hint-divider {
    display: none;
  }
}
</style>
