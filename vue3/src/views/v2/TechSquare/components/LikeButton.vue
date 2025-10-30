<template>
  <div class="like-button-container">
    <el-button
      :class="['like-button', { 'liked': isLiked, 'animating': isAnimating }]"
      :loading="loading"
      :disabled="disabled"
      @click="handleLikeClick"
      text
    >
      <span class="like-icon">{{ isLiked ? '❤️' : '🤍' }}</span>
      <span class="like-text">{{ likeText }}</span>
      <span class="like-count">{{ formattedCount }}</span>
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  toggleLike,
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
  initialLiked: {
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
const emit = defineEmits(['like-change', 'login-required'])

// ==================== 响应式数据 ====================
const userStore = useUserStore()
const loading = ref(false)
const isLiked = ref(props.initialLiked)
const likeCount = ref(props.initialCount)
const isAnimating = ref(false)

// ==================== 计算属性 ====================
const formattedCount = computed(() => {
  return formatInteractionCount(likeCount.value)
})

const likeText = computed(() => {
  return isLiked.value ? '已点赞' : '点赞'
})

const isLoggedIn = computed(() => {
  return !!userStore.token
})

// ==================== 🔥 修复：监听全局状态变化 ====================
const handleGlobalUpdate = (event) => {
  const { documentId, data } = event.detail
  if (documentId == props.documentId) {
    if (data.is_liked !== undefined) {
      isLiked.value = data.is_liked
    }
    if (data.like_count !== undefined) {
      likeCount.value = data.like_count
    }
  }
}

// ==================== 生命周期 ====================
onMounted(() => {
  // 🔥 修复：组件挂载时检查缓存状态
  const cached = getDocumentCache(props.documentId)
  if (cached && isLoggedIn.value) {
    if (cached.is_liked !== undefined) {
      isLiked.value = cached.is_liked
    }
    if (cached.like_count !== undefined) {
      likeCount.value = cached.like_count
    }
  }

  // 监听全局状态更新
  window.addEventListener('documentInteractionUpdate', handleGlobalUpdate)
})

onUnmounted(() => {
  window.removeEventListener('documentInteractionUpdate', handleGlobalUpdate)
})

// ==================== 监听器 ====================
watch(() => props.initialLiked, (newVal) => {
  // 🔥 修复：只在没有缓存时使用初始值
  const cached = getDocumentCache(props.documentId)
  if (!cached || !isLoggedIn.value) {
    isLiked.value = newVal
  }
})

watch(() => props.initialCount, (newVal) => {
  // 🔥 修复：只在没有缓存时使用初始值
  const cached = getDocumentCache(props.documentId)
  if (!cached) {
    likeCount.value = newVal
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
    isLiked.value = false
    return
  }

  try {
    const cached = getDocumentCache(props.documentId)
    if (cached && cached.is_liked !== undefined) {
      isLiked.value = cached.is_liked
      likeCount.value = cached.like_count || likeCount.value
    }
  } catch (error) {
    console.warn('加载点赞状态失败:', error)
  }
}

/**
 * 处理点赞按钮点击
 */
const handleLikeClick = async () => {
  if (!isLoggedIn.value) {
    handleLoginRequired()
    return
  }

  if (loading.value) return

  await performLikeAction()
}

/**
 * 处理未登录状态
 */
const handleLoginRequired = async () => {
  try {
    await ElMessageBox.confirm(
      '需要登录才能点赞文档',
      '登录提示',
      {
        confirmButtonText: '去登录',
        cancelButtonText: '取消',
        type: 'info',
        center: true
      }
    )

    emit('login-required', {
      type: 'like',
      documentId: props.documentId,
      action: 'toggle'
    })

  } catch {
    // 用户取消登录
  }
}

/**
 * 🔥 修复：执行点赞操作
 */
const performLikeAction = async () => {
  loading.value = true

  const originalLiked = isLiked.value
  const originalCount = likeCount.value

  try {
    // 乐观更新UI
    isLiked.value = !originalLiked
    likeCount.value = originalLiked ? originalCount - 1 : originalCount + 1

    // 触发动画
    triggerAnimation()

    // 调用API
    const response = await toggleLike(props.documentId)

    // 🔥 修复：使用服务器返回的准确数据
    const newLiked = response.is_liked
    const newCount = response.like_count

    isLiked.value = newLiked
    likeCount.value = newCount

    // 🔥 修复：更新全局缓存，同步到其他组件
    updateDocumentCache(props.documentId, {
      is_liked: newLiked,
      like_count: newCount
    })

    // 发送状态变化事件
    emit('like-change', {
      documentId: props.documentId,
      isLiked: newLiked,
      likeCount: newCount,
      message: response.message
    })

    ElMessage.success(response.message || (newLiked ? '点赞成功' : '取消点赞成功'))

  } catch (error) {
    // 回滚UI状态
    isLiked.value = originalLiked
    likeCount.value = originalCount

    console.error('点赞操作失败:', error)

    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      emit('login-required', { type: 'like', documentId: props.documentId })
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
 * 触发点赞动画
 */
const triggerAnimation = () => {
  if (isLiked.value) {
    isAnimating.value = true
    setTimeout(() => {
      isAnimating.value = false
    }, 600)
  }
}

/**
 * 外部调用：更新点赞状态
 */
const updateLikeStatus = (liked, count) => {
  isLiked.value = liked
  likeCount.value = count

  // 🔥 修复：同时更新缓存
  updateDocumentCache(props.documentId, {
    is_liked: liked,
    like_count: count
  })
}

// ==================== 暴露给父组件 ====================
defineExpose({
  updateLikeStatus,
  performLikeAction,
  loadCurrentStatus
})
</script>

<style scoped>
/* 样式保持不变 */
.like-button-container {
  display: inline-block;
}

.like-button {
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

.like-button:hover {
  border-color: #007AFF;
  color: #007AFF;
  background: #f0f8ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.15);
}

.like-button.liked {
  border-color: #ff4757;
  color: #ff4757;
  background: #fff5f5;
}

.like-button.liked:hover {
  border-color: #ff3742;
  color: #ff3742;
  background: #ffe8ea;
}

.like-button:active {
  transform: translateY(0);
}

.like-button.animating .like-icon {
  animation: likeAnimation 0.6s ease;
}

.like-icon {
  font-size: 16px;
  transition: transform 0.2s ease;
}

.like-text {
  font-size: 14px;
  white-space: nowrap;
}

.like-count {
  font-size: 13px;
  font-weight: 600;
  color: inherit;
}

/* 点赞动画 */
@keyframes likeAnimation {
  0% { transform: scale(1); }
  15% { transform: scale(1.3); }
  30% { transform: scale(1.1); }
  45% { transform: scale(1.25); }
  60% { transform: scale(1.05); }
  75% { transform: scale(1.15); }
  100% { transform: scale(1); }
}

/* 尺寸变体 */
.like-button.small {
  padding: 6px 10px;
  font-size: 12px;
  min-width: 70px;
}

.like-button.small .like-icon {
  font-size: 14px;
}

.like-button.small .like-text {
  font-size: 12px;
}

.like-button.small .like-count {
  font-size: 11px;
}

.like-button.large {
  padding: 10px 16px;
  font-size: 16px;
  min-width: 100px;
}

.like-button.large .like-icon {
  font-size: 18px;
}

.like-button.large .like-text {
  font-size: 16px;
}

.like-button.large .like-count {
  font-size: 15px;
}

/* 禁用状态 */
.like-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.like-button:disabled:hover {
  border-color: #e1e4e8;
  color: #656d76;
  background: #ffffff;
  box-shadow: none;
}

/* 响应式 */
@media (max-width: 768px) {
  .like-button {
    padding: 6px 10px;
    font-size: 13px;
    min-width: 70px;
  }

  .like-icon {
    font-size: 14px;
  }

  .like-text {
    font-size: 13px;
  }

  .like-count {
    font-size: 12px;
  }
}
</style>
