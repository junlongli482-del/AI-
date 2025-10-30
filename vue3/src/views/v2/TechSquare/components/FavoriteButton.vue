<template>
  <div class="favorite-button-container">
    <el-button
      :class="['favorite-button', { 'favorited': isFavorited }]"
      :loading="loading"
      :disabled="disabled"
      @mousedown="handleMouseDown"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
      @touchstart="handleTouchStart"
      @touchend="handleTouchEnd"
      text
    >
      <span class="favorite-icon">{{ isFavorited ? '⭐' : '☆' }}</span>
      <span class="favorite-text">{{ favoriteText }}</span>
      <span class="favorite-count">{{ formattedCount }}</span>
    </el-button>

    <!-- 功能开发中提示对话框 -->
    <el-dialog
      v-model="showFeatureDialog"
      title="功能提示"
      width="400px"
      center
    >
      <div class="feature-dialog-content">
        <div class="feature-icon">🚧</div>
        <h3>收藏夹分类功能开发中</h3>
        <p>当前版本支持统一收藏列表，收藏夹分类功能正在开发中，敬请期待！</p>
        <p class="tip">💡 提示：点击收藏按钮可直接收藏到默认列表</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="showFeatureDialog = false">
          知道了
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  toggleFavorite,
  formatInteractionCount,
  updateDocumentCache,
  getDocumentCache
} from '@/api/v2/interaction'

// ==================== Props ====================
const props = defineProps({
  documentId: {
    type: [Number, String],
    required: true
  },
  initialFavorited: {
    type: Boolean,
    default: false
  },
  initialCount: {
    type: Number,
    default: 0
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
const emit = defineEmits(['favorite-change', 'login-required'])

// ==================== 响应式数据 ====================
const userStore = useUserStore()
const loading = ref(false)
const isFavorited = ref(props.initialFavorited)
const favoriteCount = ref(props.initialCount)
const showFeatureDialog = ref(false)

// 长按相关
const pressTimer = ref(null)
const isLongPress = ref(false)

// ==================== 计算属性 ====================
const formattedCount = computed(() => {
  return formatInteractionCount(favoriteCount.value)
})

const favoriteText = computed(() => {
  return isFavorited.value ? '已收藏' : '收藏'
})

const isLoggedIn = computed(() => {
  return !!userStore.token
})

// ==================== 🔥 修复：监听全局状态变化 ====================
const handleGlobalUpdate = (event) => {
  const { documentId, data } = event.detail
  if (documentId == props.documentId) {
    if (data.is_favorited !== undefined) {
      isFavorited.value = data.is_favorited
    }
    if (data.favorite_count !== undefined) {
      favoriteCount.value = data.favorite_count
    }
  }
}

// ==================== 生命周期 ====================
onMounted(() => {
  // 🔥 修复：组件挂载时检查缓存状态
  const cached = getDocumentCache(props.documentId)
  if (cached && isLoggedIn.value) {
    if (cached.is_favorited !== undefined) {
      isFavorited.value = cached.is_favorited
    }
    if (cached.favorite_count !== undefined) {
      favoriteCount.value = cached.favorite_count
    }
  }

  // 监听全局状态更新
  window.addEventListener('documentInteractionUpdate', handleGlobalUpdate)
})

onUnmounted(() => {
  window.removeEventListener('documentInteractionUpdate', handleGlobalUpdate)
})

// ==================== 监听器 ====================
watch(() => props.initialFavorited, (newVal) => {
  // 🔥 修复：只在没有缓存时使用初始值
  const cached = getDocumentCache(props.documentId)
  if (!cached || !isLoggedIn.value) {
    isFavorited.value = newVal
  }
})

watch(() => props.initialCount, (newVal) => {
  // 🔥 修复：只在没有缓存时使用初始值
  const cached = getDocumentCache(props.documentId)
  if (!cached) {
    favoriteCount.value = newVal
  }
})

// 🔥 修复：监听用户登录状态变化
watch(() => userStore.token, (newToken, oldToken) => {
  if (newToken !== oldToken) {
    // 用户登录状态变化，重新获取状态
    loadCurrentStatus()
  }
})

// ==================== 方法 ====================

/**
 * 🔥 新增：加载当前状态
 */
const loadCurrentStatus = async () => {
  if (!isLoggedIn.value) {
    // 未登录时使用初始值
    isFavorited.value = false
    return
  }

  try {
    const cached = getDocumentCache(props.documentId)
    if (cached && cached.is_favorited !== undefined) {
      isFavorited.value = cached.is_favorited
      favoriteCount.value = cached.favorite_count || favoriteCount.value
    }
  } catch (error) {
    console.warn('加载收藏状态失败:', error)
  }
}

/**
 * 鼠标按下事件
 */
const handleMouseDown = (event) => {
  // 只处理左键
  if (event.button !== 0) return

  startPressTimer()
}

/**
 * 鼠标抬起事件
 */
const handleMouseUp = () => {
  handlePressEnd()
}

/**
 * 鼠标离开事件
 */
const handleMouseLeave = () => {
  clearPressTimer()
}

/**
 * 触摸开始事件
 */
const handleTouchStart = () => {
  startPressTimer()
}

/**
 * 触摸结束事件
 */
const handleTouchEnd = () => {
  handlePressEnd()
}

/**
 * 开始长按计时
 */
const startPressTimer = () => {
  isLongPress.value = false
  clearPressTimer()

  pressTimer.value = setTimeout(() => {
    isLongPress.value = true
    handleLongPress()
  }, 1000) // 1秒长按
}

/**
 * 清除长按计时
 */
const clearPressTimer = () => {
  if (pressTimer.value) {
    clearTimeout(pressTimer.value)
    pressTimer.value = null
  }
}

/**
 * 处理按压结束
 */
const handlePressEnd = () => {
  clearPressTimer()

  // 如果不是长按，执行普通点击
  if (!isLongPress.value) {
    handleFavoriteClick()
  }

  isLongPress.value = false
}

/**
 * 处理长按事件
 */
const handleLongPress = () => {
  // 触发震动反馈（如果支持）
  if (navigator.vibrate) {
    navigator.vibrate(50)
  }

  // 显示功能开发中对话框
  showFeatureDialog.value = true
}

/**
 * 处理收藏按钮点击
 */
const handleFavoriteClick = async () => {
  // 检查登录状态
  if (!isLoggedIn.value) {
    handleLoginRequired()
    return
  }

  // 防止重复点击
  if (loading.value) return

  await performFavoriteAction()
}

/**
 * 处理未登录状态
 */
const handleLoginRequired = async () => {
  try {
    await ElMessageBox.confirm(
      '需要登录才能收藏文档',
      '登录提示',
      {
        confirmButtonText: '去登录',
        cancelButtonText: '取消',
        type: 'info',
        center: true
      }
    )

    // 发送登录需求事件
    emit('login-required', {
      type: 'favorite',
      documentId: props.documentId,
      action: 'toggle'
    })

  } catch {
    // 用户取消登录
  }
}

/**
 * 🔥 修复：执行收藏操作
 */
const performFavoriteAction = async () => {
  loading.value = true

  // 保存原始状态，用于失败时回滚
  const originalFavorited = isFavorited.value
  const originalCount = favoriteCount.value

  try {
    // 乐观更新UI
    isFavorited.value = !originalFavorited
    favoriteCount.value = originalFavorited ? originalCount - 1 : originalCount + 1

    // 调用API
    const response = await toggleFavorite(props.documentId)

    // 🔥 修复：使用服务器返回的准确数据
    const newFavorited = response.is_favorited
    const newCount = response.favorite_count

    isFavorited.value = newFavorited
    favoriteCount.value = newCount

    // 🔥 修复：更新全局缓存，同步到其他组件
    updateDocumentCache(props.documentId, {
      is_favorited: newFavorited,
      favorite_count: newCount
    })

    // 发送状态变化事件
    emit('favorite-change', {
      documentId: props.documentId,
      isFavorited: newFavorited,
      favoriteCount: newCount,
      message: response.message
    })

    // 显示成功提示
    ElMessage.success(response.message || (newFavorited ? '收藏成功' : '取消收藏成功'))

  } catch (error) {
    // 回滚UI状态
    isFavorited.value = originalFavorited
    favoriteCount.value = originalCount

    console.error('收藏操作失败:', error)

    // 显示错误提示
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      emit('login-required', { type: 'favorite', documentId: props.documentId })
    } else if (error.response?.status === 404) {
      ElMessage.error('文档不存在')
    } else {
      ElMessage.error('操作失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 外部调用：更新收藏状态
 */
const updateFavoriteStatus = (favorited, count) => {
  isFavorited.value = favorited
  favoriteCount.value = count

  // 🔥 修复：同时更新缓存
  updateDocumentCache(props.documentId, {
    is_favorited: favorited,
    favorite_count: count
  })
}

// ==================== 暴露给父组件 ====================
defineExpose({
  updateFavoriteStatus,
  performFavoriteAction,
  loadCurrentStatus
})
</script>

<style scoped>
.favorite-button-container {
  display: inline-block;
}

.favorite-button {
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
  user-select: none; /* 防止长按时选中文本 */
}

.favorite-button:hover {
  border-color: #ffa500;
  color: #ffa500;
  background: #fff8f0;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 165, 0, 0.15);
}

.favorite-button.favorited {
  border-color: #ffa500;
  color: #ffa500;
  background: #fff8f0;
}

.favorite-button.favorited:hover {
  border-color: #ff8c00;
  color: #ff8c00;
  background: #fff0e6;
}

.favorite-button:active {
  transform: translateY(0);
}

.favorite-icon {
  font-size: 16px;
  transition: transform 0.2s ease;
}

.favorite-text {
  font-size: 14px;
  white-space: nowrap;
}

.favorite-count {
  font-size: 13px;
  font-weight: 600;
  color: inherit;
}

/* 功能提示对话框样式 */
.feature-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-dialog-content h3 {
  color: #24292f;
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
}

.feature-dialog-content p {
  color: #656d76;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.feature-dialog-content .tip {
  color: #007AFF;
  font-size: 14px;
  background: #f0f8ff;
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 16px;
}

/* 尺寸变体 */
.favorite-button.small {
  padding: 6px 10px;
  font-size: 12px;
  min-width: 70px;
}

.favorite-button.small .favorite-icon {
  font-size: 14px;
}

.favorite-button.small .favorite-text {
  font-size: 12px;
}

.favorite-button.small .favorite-count {
  font-size: 11px;
}

.favorite-button.large {
  padding: 10px 16px;
  font-size: 16px;
  min-width: 100px;
}

.favorite-button.large .favorite-icon {
  font-size: 18px;
}

.favorite-button.large .favorite-text {
  font-size: 16px;
}

.favorite-button.large .favorite-count {
  font-size: 15px;
}

/* 禁用状态 */
.favorite-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.favorite-button:disabled:hover {
  border-color: #e1e4e8;
  color: #656d76;
  background: #ffffff;
  box-shadow: none;
}

/* 响应式 */
@media (max-width: 768px) {
  .favorite-button {
    padding: 6px 10px;
    font-size: 13px;
    min-width: 70px;
  }

  .favorite-icon {
    font-size: 14px;
  }

  .favorite-text {
    font-size: 13px;
  }

  .favorite-count {
    font-size: 12px;
  }
}
</style>
