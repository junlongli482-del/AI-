<template>
  <div class="share-button-container">
    <el-button
      class="share-button"
      :loading="loading"
      :disabled="disabled"
      @click="handleShareClick"
      text
    >
      <span class="share-icon">📤</span>
      <span class="share-text">分享</span>
    </el-button>

    <!-- 分享对话框 -->
    <el-dialog
      v-model="showShareDialog"
      title="分享文档"
      width="500px"
      center
      :close-on-click-modal="false"
    >
      <div class="share-dialog-content">
        <div class="document-info">
          <h4>{{ documentTitle }}</h4>
          <p>作者：{{ authorName }}</p>
        </div>

        <div class="share-link-section">
          <label>分享链接：</label>
          <div class="link-input-group">
            <el-input
              v-model="shareUrl"
              readonly
              placeholder="生成分享链接中..."
            >
              <template #suffix>
                <el-icon v-if="generating" class="is-loading">
                  <Loading />
                </el-icon>
              </template>
            </el-input>
            <el-button
              @click="copyShareLink"
              type="primary"
              :disabled="!shareUrl || generating"
            >
              复制链接
            </el-button>
          </div>
        </div>

        <div class="share-tips">
          <p>💡 提示：此链接为前端访问链接，任何人都可以通过此链接查看文档</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="showShareDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

// ==================== Props ====================
const props = defineProps({
  documentId: {
    type: [Number, String],
    required: true
  },
  documentTitle: {
    type: String,
    default: '未知文档'
  },
  authorName: {
    type: String,
    default: '未知作者'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'default',
    validator: (value) => ['small', 'default', 'large'].includes(value)
  }
})

// ==================== Emits ====================
const emit = defineEmits(['share-success'])

// ==================== 响应式数据 ====================
const loading = ref(false)
const showShareDialog = ref(false)
const shareUrl = ref('')
const generating = ref(false)

// ==================== 计算属性 ====================
const documentTitle = computed(() => {
  return props.documentTitle || '未知文档'
})

const authorName = computed(() => {
  return props.authorName || '未知作者'
})

// ==================== 方法 ====================

/**
 * 处理分享按钮点击
 */
const handleShareClick = async () => {
  if (loading.value) return

  showShareDialog.value = true
  await generateShareLink()
}

/**
 * 生成分享链接
 */
const generateShareLink = async () => {
  generating.value = true
  shareUrl.value = ''

  try {
    // 模拟生成过程（实际项目中可能需要调用API）
    await new Promise(resolve => setTimeout(resolve, 500))

    // 生成前端访问链接
    const baseUrl = window.location.origin
    shareUrl.value = `${baseUrl}/tech-square/document/${props.documentId}`

    ElMessage.success('分享链接生成成功')

  } catch (error) {
    console.error('生成分享链接失败:', error)
    ElMessage.error('生成分享链接失败')
  } finally {
    generating.value = false
  }
}

/**
 * 复制分享链接
 */
const copyShareLink = async () => {
  if (!shareUrl.value) {
    ElMessage.warning('分享链接还未生成')
    return
  }

  try {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('分享链接已复制到剪贴板')

    // 发送分享成功事件
    emit('share-success', {
      documentId: props.documentId,
      shareUrl: shareUrl.value,
      method: 'copy'
    })

  } catch (error) {
    // 降级方案：使用传统方法复制
    try {
      const textArea = document.createElement('textarea')
      textArea.value = shareUrl.value
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)

      ElMessage.success('分享链接已复制到剪贴板')

      emit('share-success', {
        documentId: props.documentId,
        shareUrl: shareUrl.value,
        method: 'copy'
      })

    } catch (fallbackError) {
      console.error('复制失败:', fallbackError)
      ElMessage.error('复制失败，请手动选择复制')
    }
  }
}

/**
 * 外部调用：打开分享对话框
 */
const openShareDialog = () => {
  handleShareClick()
}

// ==================== 暴露给父组件 ====================
defineExpose({
  openShareDialog
})
</script>

<style scoped>
.share-button-container {
  display: inline-block;
}

.share-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
  background: #ffffff;
  color: #656d76;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  min-width: 80px;
  justify-content: center;
}

.share-button:hover {
  border-color: #007AFF;
  color: #007AFF;
  background: #f0f8ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.15);
}

.share-button:active {
  transform: translateY(0);
}

.share-icon {
  font-size: 16px;
  transition: transform 0.2s ease;
}

.share-text {
  font-size: 14px;
  white-space: nowrap;
}

/* 分享对话框样式 */
.share-dialog-content {
  padding: 10px 0;
}

.document-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.document-info h4 {
  margin: 0 0 8px 0;
  color: #24292f;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.document-info p {
  margin: 0;
  color: #656d76;
  font-size: 14px;
}

.share-link-section {
  margin-bottom: 20px;
}

.share-link-section label {
  display: block;
  margin-bottom: 8px;
  color: #24292f;
  font-weight: 500;
  font-size: 14px;
}

.link-input-group {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.link-input-group .el-input {
  flex: 1;
}

.share-tips {
  padding: 12px 16px;
  background: #e3f2fd;
  border-radius: 6px;
  border-left: 4px solid #007AFF;
}

.share-tips p {
  margin: 0;
  color: #1565c0;
  font-size: 13px;
  line-height: 1.4;
}

/* 尺寸变体 */
.share-button.small {
  padding: 6px 10px;
  font-size: 12px;
  min-width: 70px;
}

.share-button.small .share-icon {
  font-size: 14px;
}

.share-button.small .share-text {
  font-size: 12px;
}

.share-button.large {
  padding: 10px 16px;
  font-size: 16px;
  min-width: 100px;
}

.share-button.large .share-icon {
  font-size: 18px;
}

.share-button.large .share-text {
  font-size: 16px;
}

/* 禁用状态 */
.share-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.share-button:disabled:hover {
  border-color: #e1e4e8;
  color: #656d76;
  background: #ffffff;
  box-shadow: none;
}

/* 加载图标动画 */
.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .share-button {
    padding: 6px 10px;
    font-size: 13px;
    min-width: 70px;
  }

  .share-icon {
    font-size: 14px;
  }

  .share-text {
    font-size: 13px;
  }

  .link-input-group {
    flex-direction: column;
    gap: 8px;
  }

  .link-input-group .el-button {
    width: 100%;
  }

  :deep(.el-dialog) {
    width: 90% !important;
    margin: 0 auto;
  }
}
</style>
