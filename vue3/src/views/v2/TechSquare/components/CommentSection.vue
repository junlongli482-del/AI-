<template>
  <div class="comment-section">
    <!-- 评论标题和统计 -->
    <div class="comment-header">
      <div class="comment-title-wrapper">
        <h3 class="comment-title">
          <span class="comment-icon">💬</span>
          <span class="title-gradient">评论</span>
          <span class="comment-count-badge">{{ totalComments }}</span>
        </h3>
        <div class="comment-sort">
          <span class="sort-text">按时间排序</span>
          <el-icon class="sort-icon"><Clock /></el-icon>
        </div>
      </div>
    </div>

    <!-- 发表评论区域 -->
    <div class="comment-compose">
      <div class="compose-glow"></div>
      <div class="compose-avatar">
        <div class="avatar-circle">👤</div>
      </div>

      <div class="compose-content">
        <div class="compose-input-wrapper">
          <div class="input-glow"></div>
          <el-input
            ref="commentInputRef"
            v-model="commentContent"
            type="textarea"
            :rows="3"
            placeholder="写下你的想法..."
            :maxlength="1000"
            show-word-limit
            resize="none"
            class="compose-textarea"
            @keydown="handleKeydown"
            @focus="handleInputFocus"
            @blur="handleInputBlur"
          />
        </div>

        <div class="compose-toolbar" :class="{ 'focused': isInputFocused }">
          <div class="toolbar-left">
            <EmojiPicker @emoji-select="handleEmojiSelect" />
            <span class="compose-tip">💡 Ctrl+Enter 快速发表</span>
          </div>

          <div class="toolbar-right">
            <el-button
              @click="clearComment"
              :disabled="!commentContent.trim()"
              class="clear-btn"
              text
            >
              清空
            </el-button>
            <button
              @click="submitComment"
              :disabled="!commentContent.trim() || submitting"
              class="fancy-submit-btn"
            >
              <div class="btn-bg"></div>
              <div class="btn-shine"></div>
              <div class="btn-content">
                <span v-if="!submitting">🚀 发表评论</span>
                <span v-else>
                  <svg class="loading-spinner" viewBox="0 0 24 24" width="16" height="16">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                      <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                      <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                    </circle>
                  </svg>
                  发表中...
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comment-list">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="comment-skeleton" v-for="i in 3" :key="i">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-content">
            <div class="skeleton-line skeleton-name"></div>
            <div class="skeleton-line skeleton-text"></div>
            <div class="skeleton-line skeleton-text short"></div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="comments.length === 0" class="empty-container">
        <div class="empty-shapes">
          <div class="empty-shape shape-1"></div>
          <div class="empty-shape shape-2"></div>
          <div class="empty-shape shape-3"></div>
        </div>
        <div class="empty-icon">💭</div>
        <div class="empty-text">还没有评论</div>
        <div class="empty-subtext">来发表第一条评论吧！</div>
      </div>

      <!-- 评论项 -->
      <div v-else class="comments-container">
        <CommentItem
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          :document-author-id="documentAuthorId"
          @reply="handleReply"
          @delete="handleDeleteComment"
          @login-required="handleLoginRequired"
        />
      </div>

      <!-- 分页加载 -->
      <div v-if="hasMore && !loading" class="load-more-container">
        <button
          @click="loadMoreComments"
          :disabled="loadingMore"
          class="load-more-btn"
        >
          <div class="load-more-bg"></div>
          <div class="load-more-content">
            <span v-if="!loadingMore">✨ 查看更多评论</span>
            <span v-else>加载中...</span>
          </div>
        </button>
      </div>
    </div>

    <!-- 回复对话框 -->
    <el-dialog
      v-model="showReplyDialog"
      :title="`回复 @${replyTarget?.user?.nickname || replyTarget?.user?.username}`"
      width="600px"
      center
      class="reply-dialog"
      @opened="handleReplyDialogOpened"
    >
      <div class="reply-dialog-content">
        <!-- 原评论引用 -->
        <div class="original-comment">
          <div class="original-glow"></div>
          <div class="original-header">
            <div class="original-avatar">👤</div>
            <div class="original-info">
              <span class="original-author">{{ replyTarget?.user?.nickname || replyTarget?.user?.username }}</span>
              <span class="original-time">{{ formatCommentTime(replyTarget?.created_at) }}</span>
            </div>
          </div>
          <div class="original-content">{{ replyTarget?.content }}</div>
        </div>

        <!-- 回复输入 -->
        <div class="reply-input-section">
          <div class="reply-avatar">
            <div class="avatar-circle">👤</div>
          </div>
          <div class="reply-input-wrapper">
            <div class="input-glow"></div>
            <el-input
              ref="replyInputRef"
              v-model="replyContent"
              type="textarea"
              :rows="4"
              placeholder="写下你的回复..."
              :maxlength="1000"
              show-word-limit
              resize="none"
              class="reply-textarea"
            />

            <div class="reply-toolbar">
              <EmojiPicker @emoji-select="handleReplyEmojiSelect" />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelReply" class="cancel-btn">取消</el-button>
          <button
            @click="submitReply"
            :disabled="!replyContent.trim() || submitting"
            class="fancy-reply-btn"
          >
            <div class="btn-bg"></div>
            <div class="btn-shine"></div>
            <div class="btn-content">
              <span v-if="!submitting">🎯 发表回复</span>
              <span v-else>回复中...</span>
            </div>
          </button>
        </div>
      </template>
    </el-dialog>

    <!-- 登录提示对话框 -->
    <el-dialog
      v-model="showLoginDialog"
      title="需要登录"
      width="400px"
      center
      class="login-dialog"
    >
      <div class="login-dialog-content">
        <div class="login-icon">🔐</div>
        <p class="login-message">{{ loginMessage }}</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showLoginDialog = false">取消</el-button>
          <el-button type="primary" @click="goToLogin">去登录</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import CommentItem from './CommentItem.vue'
import EmojiPicker from './EmojiPicker.vue'
import {
  getComments,
  createComment,
  deleteComment,
  validateCommentContent
} from '@/api/v2/interaction'

// ==================== Props ====================
const props = defineProps({
  documentId: {
    type: [Number, String],
    required: true
  },
  documentAuthorId: {
    type: [Number, String],
    default: null
  },
  initialCommentCount: {
    type: Number,
    default: 0
  }
})

// ==================== Emits ====================
const emit = defineEmits(['comment-count-change', 'login-required'])

// ==================== 响应式数据 ====================
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const loadingMore = ref(false)
const submitting = ref(false)
const comments = ref([])
const totalComments = ref(props.initialCommentCount)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const hasMore = computed(() => comments.value.length < totalComments.value)

// 评论输入
const commentContent = ref('')
const commentInputRef = ref(null)
const isInputFocused = ref(false)

// 回复相关
const showReplyDialog = ref(false)
const replyTarget = ref(null)
const replyContent = ref('')
const replyInputRef = ref(null)

// 登录对话框
const showLoginDialog = ref(false)
const loginMessage = ref('')

// 计算属性
const isLoggedIn = computed(() => !!userStore.token)

// ==================== 生命周期 ====================
onMounted(() => {
  loadComments()
})

// 监听文档ID变化
watch(() => props.documentId, () => {
  resetComments()
  loadComments()
})

// ==================== 方法 ====================

/**
 * 格式化评论时间
 */
const formatCommentTime = (dateString) => {
  if (!dateString) return '未知时间'

  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

/**
 * 输入框聚焦处理
 */
const handleInputFocus = () => {
  isInputFocused.value = true
}

const handleInputBlur = () => {
  isInputFocused.value = false
}

/**
 * 回复对话框打开后自动聚焦
 */
const handleReplyDialogOpened = async () => {
  await nextTick()
  if (replyInputRef.value) {
    replyInputRef.value.focus()
  }
}

/**
 * 重置评论数据
 */
const resetComments = () => {
  comments.value = []
  currentPage.value = 1
  totalComments.value = props.initialCommentCount
}

/**
 * 加载评论列表
 */
const loadComments = async (page = 1, append = false) => {
  if (!append) {
    loading.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const response = await getComments(props.documentId, {
      page,
      size: pageSize.value
    })

    if (append) {
      comments.value.push(...(response.items || []))
    } else {
      comments.value = response.items || []
    }

    totalComments.value = response.total || 0
    currentPage.value = response.page || 1

    // 通知父组件评论数量变化
    emit('comment-count-change', totalComments.value)

  } catch (error) {
    console.error('加载评论失败:', error)
    ElMessage.error('加载评论失败')
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

/**
 * 加载更多评论
 */
const loadMoreComments = () => {
  const nextPage = currentPage.value + 1
  loadComments(nextPage, true)
}

/**
 * 处理键盘事件
 */
const handleKeydown = (event) => {
  // Ctrl+Enter 快速发表
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    submitComment()
  }
}

/**
 * 处理表情选择
 */
const handleEmojiSelect = (emoji) => {
  commentContent.value += emoji
  // 选择表情后重新聚焦输入框
  nextTick(() => {
    if (commentInputRef.value) {
      commentInputRef.value.focus()
    }
  })
}

/**
 * 清空评论
 */
const clearComment = () => {
  commentContent.value = ''
  if (commentInputRef.value) {
    commentInputRef.value.focus()
  }
}

/**
 * 提交评论
 */
const submitComment = async () => {
  // 检查登录状态
  if (!isLoggedIn.value) {
    handleLoginRequired('需要登录才能发表评论')
    return
  }

  // 验证评论内容
  const validation = validateCommentContent(commentContent.value)
  if (!validation.valid) {
    ElMessage.warning(validation.message)
    return
  }

  submitting.value = true

  try {
    const response = await createComment(props.documentId, {
      content: commentContent.value.trim(),
      parent_id: null
    })

    // 添加新评论到列表顶部（按时间倒序）
    comments.value.unshift(response.comment)
    totalComments.value += 1

    // 清空输入框
    commentContent.value = ''

    // 通知父组件
    emit('comment-count-change', totalComments.value)

    ElMessage.success('评论发表成功')

  } catch (error) {
    console.error('发表评论失败:', error)

    if (error.response?.status === 401) {
      handleLoginRequired('登录已过期，请重新登录')
    } else {
      ElMessage.error('发表评论失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

/**
 * 处理回复 - 自动聚焦
 */
const handleReply = (comment) => {
  // 检查登录状态
  if (!isLoggedIn.value) {
    handleLoginRequired('需要登录才能回复评论')
    return
  }

  replyTarget.value = comment
  replyContent.value = ''
  showReplyDialog.value = true
}

/**
 * 处理回复表情选择
 */
const handleReplyEmojiSelect = (emoji) => {
  replyContent.value += emoji
  nextTick(() => {
    if (replyInputRef.value) {
      replyInputRef.value.focus()
    }
  })
}

/**
 * 取消回复
 */
const cancelReply = () => {
  showReplyDialog.value = false
  replyTarget.value = null
  replyContent.value = ''
}

/**
 * 提交回复
 */
const submitReply = async () => {
  // 验证回复内容
  const validation = validateCommentContent(replyContent.value)
  if (!validation.valid) {
    ElMessage.warning(validation.message)
    return
  }

  submitting.value = true

  try {
    const response = await createComment(props.documentId, {
      content: replyContent.value.trim(),
      parent_id: replyTarget.value.id
    })

    // 找到父评论并添加回复
    const parentComment = comments.value.find(c => c.id === replyTarget.value.id)
    if (parentComment) {
      if (!parentComment.replies) {
        parentComment.replies = []
      }
      parentComment.replies.push(response.comment)
      parentComment.reply_count = (parentComment.reply_count || 0) + 1
    }

    totalComments.value += 1

    // 关闭对话框
    cancelReply()

    // 通知父组件
    emit('comment-count-change', totalComments.value)

    ElMessage.success('回复发表成功')

  } catch (error) {
    console.error('发表回复失败:', error)

    if (error.response?.status === 401) {
      handleLoginRequired('登录已过期，请重新登录')
    } else {
      ElMessage.error('发表回复失败，请稍后重试')
    }
  } finally {
    submitting.value = false
  }
}

/**
 * 处理删除评论
 */
const handleDeleteComment = async (comment, isReply = false, parentComment = null) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条${isReply ? '回复' : '评论'}吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteComment(comment.id)

    if (isReply && parentComment) {
      // 删除回复
      const replyIndex = parentComment.replies.findIndex(r => r.id === comment.id)
      if (replyIndex !== -1) {
        parentComment.replies.splice(replyIndex, 1)
        parentComment.reply_count = Math.max(0, (parentComment.reply_count || 1) - 1)
      }
    } else {
      // 删除评论（包括所有回复）
      const commentIndex = comments.value.findIndex(c => c.id === comment.id)
      if (commentIndex !== -1) {
        const deletedComment = comments.value[commentIndex]
        const deletedCount = 1 + (deletedComment.reply_count || 0)

        comments.value.splice(commentIndex, 1)
        totalComments.value = Math.max(0, totalComments.value - deletedCount)
      }
    }

    // 通知父组件
    emit('comment-count-change', totalComments.value)

    ElMessage.success('删除成功')

  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评论失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

/**
 * 处理登录需求
 */
const handleLoginRequired = (message) => {
  loginMessage.value = message
  showLoginDialog.value = true
}

/**
 * 跳转到登录页
 */
const goToLogin = () => {
  showLoginDialog.value = false
  emit('login-required')
}

/**
 * 外部调用：刷新评论列表
 */
const refreshComments = () => {
  resetComments()
  loadComments()
}

// ==================== 暴露给父组件 ====================
defineExpose({
  refreshComments,
  loadComments
})
</script>

<style scoped>
.comment-section {
  margin-top: 40px;
  padding: 32px 0;
  border-top: 2px solid #f1f3f4;
}

/* 评论标题 */
.comment-header {
  margin-bottom: 32px;
}

.comment-title-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.comment-icon {
  font-size: 28px;
}

.title-gradient {
  background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #ffeaa7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.comment-count-badge {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  min-width: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(255, 154, 158, 0.3);
}

.comment-sort {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.sort-text {
  font-weight: 500;
}

.sort-icon {
  font-size: 16px;
}

/* 发表评论区域 */
.comment-compose {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 32px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  gap: 16px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.comment-compose:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.compose-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #ffeaa7, #fd79a8, #a8e6cf);
  background-size: 400% 400%;
  border-radius: 22px;
  z-index: -1;
  animation: gradientShift 6s ease infinite;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.comment-compose:hover .compose-glow {
  opacity: 0.6;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.compose-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  box-shadow: 0 4px 12px rgba(255, 154, 158, 0.4);
}

.compose-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.compose-input-wrapper {
  position: relative;
}

.input-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff9a9e, #fad0c4, #a8edea, #fed6e3);
  border-radius: 14px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.compose-input-wrapper:focus-within .input-glow {
  opacity: 1;
}

:deep(.el-textarea__inner) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 16px;
  font-size: 15px;
  line-height: 1.6;
  transition: all 0.3s ease;
  resize: none;
}

:deep(.el-textarea__inner):focus {
  background: rgba(255, 255, 255, 1);
  border-color: transparent;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

:deep(.el-input__count) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 2px 8px;
  font-size: 12px;
  color: #6b7280;
}

.compose-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.compose-toolbar.focused {
  opacity: 1;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.compose-tip {
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.clear-btn {
  color: #6b7280;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* 花哨提交按钮 */
.fancy-submit-btn {
  height: 40px;
  border: none;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  background: transparent;
  padding: 0 20px;
}

.fancy-submit-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transition: left 0.6s ease;
}

.fancy-submit-btn:hover:not(:disabled) .btn-bg {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(255, 107, 107, 0.4);
}

.fancy-submit-btn:hover:not(:disabled) .btn-shine {
  left: 100%;
}

.btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
  font-size: 14px;
  font-weight: 600;
  gap: 6px;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-skeleton {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}


.skeleton-avatar {
  width: 44px;
  height: 44px;
  background: linear-gradient(90deg, #ff9a9e 25%, #fad0c4 50%, #ff9a9e 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 50%;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #a8edea 25%, #fed6e3 50%, #a8edea 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 6px;
}

.skeleton-name {
  width: 120px;
}

.skeleton-text {
  width: 100%;
}

.skeleton-text.short {
  width: 60%;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 空状态 */
.empty-container {
  text-align: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 2px dashed rgba(255, 154, 158, 0.3);
  position: relative;
  overflow: hidden;
}

.empty-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.empty-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.empty-shape.shape-1 {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
  top: 20%;
  left: 10%;
  animation: float1 6s ease-in-out infinite;
}

.empty-shape.shape-2 {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #ffeaa7, #fd79a8);
  top: 60%;
  right: 15%;
  animation: float2 8s ease-in-out infinite;
}

.empty-shape.shape-3 {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #a8e6cf, #ff8a80);
  bottom: 20%;
  left: 20%;
  animation: float3 7s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  50% { transform: translateY(-20px) translateX(10px); }
}

@keyframes float2 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  50% { transform: translateY(-15px) translateX(-10px); }
}

@keyframes float3 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  50% { transform: translateY(-25px) translateX(15px); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
  position: relative;
  z-index: 1;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.empty-subtext {
  font-size: 14px;
  color: #6b7280;
  position: relative;
  z-index: 1;
}

/* 评论列表 */
.comments-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 加载更多按钮 */
.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.load-more-btn {
  height: 48px;
  border: none;
  border-radius: 25px;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  background: transparent;
  padding: 0 32px;
}

.load-more-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.load-more-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  border-radius: 25px;
  transition: all 0.3s ease;
}

.load-more-btn:hover:not(:disabled) .load-more-bg {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(168, 237, 234, 0.4);
}

.load-more-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
}

/* 回复对话框 */
.reply-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
}

.reply-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  padding: 20px 24px;
}

.reply-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.reply-dialog-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.original-comment {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  border: 2px solid rgba(255, 154, 158, 0.2);
  position: relative;
  overflow: hidden;
}

.original-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff9a9e, #fad0c4, #a8edea);
  background-size: 400% 400%;
  border-radius: 18px;
  z-index: -1;
  animation: gradientShift 4s ease infinite;
  opacity: 0.3;
}

.original-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.original-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: white;
  box-shadow: 0 2px 8px rgba(255, 154, 158, 0.3);
}

.original-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.original-author {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.original-time {
  font-size: 12px;
  color: #6b7280;
}

.original-content {
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
}

.reply-input-section {
  display: flex;
  gap: 16px;
}

.reply-avatar {
  flex-shrink: 0;
}

.reply-input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

:deep(.reply-textarea .el-textarea__inner) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 16px;
  font-size: 15px;
  line-height: 1.6;
  transition: all 0.3s ease;
}

:deep(.reply-textarea .el-textarea__inner):focus {
  background: rgba(255, 255, 255, 1);
  border-color: transparent;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.reply-toolbar {
  display: flex;
  justify-content: flex-start;
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 0 24px 24px 24px;
}

.cancel-btn {
  color: #6b7280;
  border-color: #d1d5db;
  border-radius: 10px;
  padding: 10px 20px;
}

.fancy-reply-btn {
  height: 40px;
  border: none;
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  background: transparent;
  padding: 0 20px;
}

.fancy-reply-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.fancy-reply-btn .btn-bg {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
}

.fancy-reply-btn:hover:not(:disabled) .btn-bg {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(78, 205, 196, 0.4);
}

/* 登录对话框 */
.login-dialog :deep(.el-dialog) {
  border-radius: 20px;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
}

.login-dialog-content {
  text-align: center;
  padding: 20px 0;
}

.login-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.login-message {
  color: #374151;
  margin: 0;
  font-size: 16px;
  line-height: 1.5;
}

/* 响应式 */
@media (max-width: 768px) {
  .comment-section {
    padding: 24px 0;
  }

  .comment-title-wrapper {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .comment-title {
    font-size: 20px;
  }

  .comment-compose {
    padding: 20px;
    flex-direction: column;
    gap: 16px;
  }

  .compose-content {
    gap: 12px;
  }

  .compose-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .toolbar-right {
    width: 100%;
  }

  .toolbar-right .clear-btn,
  .toolbar-right .fancy-submit-btn {
    flex: 1;
  }

  .compose-tip {
    display: none;
  }

  .reply-dialog-content {
    padding: 16px;
  }

  .reply-input-section {
    flex-direction: column;
    gap: 12px;
  }

  .dialog-footer {
    padding: 0 16px 16px 16px;
  }
}
</style>
