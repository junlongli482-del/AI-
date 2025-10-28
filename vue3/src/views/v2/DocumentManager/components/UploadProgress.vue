<template>
  <div class="upload-progress">
    <!-- 文件列表 -->
    <div v-if="fileList.length > 0" class="file-list">
      <div
        v-for="item in fileList"
        :key="item.id"
        class="file-item"
        :class="{ 'is-error': item.status === 'error' }"
      >
        <!-- 文件信息 -->
        <div class="file-info">
          <div class="file-icon">
            <svg v-if="item.status === 'validating'" class="icon-loading" width="20" height="20" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.25"/>
              <path d="M12 2 A10 10 0 0 1 22 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="item.status === 'validated'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#52c41a">
              <path d="M20 6L9 17l-5-5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="item.status === 'uploading'" class="icon-loading" width="20" height="20" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.25"/>
              <path d="M12 2 A10 10 0 0 1 22 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="item.status === 'success'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#52c41a">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <path d="M9 12l2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="item.status === 'error'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff4d4f">
              <circle cx="12" cy="12" r="10" stroke-width="2"/>
              <path d="M15 9l-6 6M9 9l6 6" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#656d76">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" stroke-width="2"/>
              <polyline points="13 2 13 9 20 9" stroke-width="2"/>
            </svg>
          </div>

          <div class="file-details">
            <div class="file-name">{{ item.file.name }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatSize(item.file.size) }}</span>
              <span v-if="item.status === 'validating'" class="file-status">验证中...</span>
              <span v-else-if="item.status === 'validated'" class="file-status success">验证通过</span>
              <span v-else-if="item.status === 'uploading'" class="file-status">上传中 {{ item.progress }}%</span>
              <span v-else-if="item.status === 'success'" class="file-status success">上传成功</span>
              <span v-else-if="item.status === 'error'" class="file-status error">{{ item.errorMessage }}</span>
            </div>
          </div>
        </div>

        <!-- 进度条 -->
        <div v-if="item.status === 'uploading'" class="progress-bar">
          <div class="progress-fill" :style="{ width: item.progress + '%' }"></div>
        </div>

        <!-- 操作按钮 -->
        <div class="file-actions">
          <button
            v-if="item.status === 'error' || item.status === 'validated'"
            class="btn-remove"
            @click="removeFile(item.id)"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M18 6L6 18M6 6l12 12" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <p>暂无文件</p>
    </div>
  </div>
</template>

<script setup>
import { formatFileSize } from '@/api/v2/file_upload/index'

// Props
defineProps({
  fileList: {
    type: Array,
    required: true,
    default: () => []
  }
})

// 事件定义
const emit = defineEmits(['remove-file'])

// 格式化文件大小
const formatSize = (bytes) => {
  return formatFileSize(bytes)
}

// 移除文件
const removeFile = (fileId) => {
  emit('remove-file', fileId)
}
</script>

<style scoped>
.upload-progress {
  width: 100%;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.file-item:hover {
  border-color: #007AFF;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.1);
}

.file-item.is-error {
  border-color: #ff4d4f;
  background: #fff2f0;
}

.file-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.file-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f6f8fa;
  border-radius: 8px;
}

.icon-loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #24292f;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #656d76;
}

.file-size {
  color: #656d76;
}

.file-status {
  color: #656d76;
}

.file-status.success {
  color: #52c41a;
}

.file-status.error {
  color: #ff4d4f;
}

.progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #f0f0f0;
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007AFF, #00C6FF);
  transition: width 0.3s ease;
}

.file-actions {
  flex-shrink: 0;
}

.btn-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #656d76;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-remove:hover {
  background: #f6f8fa;
  color: #ff4d4f;
}

.empty-state {
  padding: 32px;
  text-align: center;
  color: #656d76;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .file-item {
    padding: 12px;
  }

  .file-icon {
    width: 36px;
    height: 36px;
  }

  .file-name {
    font-size: 13px;
  }

  .file-meta {
    font-size: 12px;
  }
}
</style>
