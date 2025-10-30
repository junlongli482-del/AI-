<template>
  <div class="comment-item">
    <div class="comment-glow"></div>

    <!-- 主评论 -->
    <div class="comment-main">
      <div class="comment-avatar">
        <div class="avatar-circle">👤</div>
      </div>

      <div class="comment-content-wrapper">
        <!-- 用户信息和时间 -->
        <div class="comment-header">
          <div class="user-info">
            <span class="user-name">{{ getUserDisplayName(comment.user) }}</span>
            <span v-if="isDocumentAuthor(comment.user.id)" class="author-badge">作者</span>
            <span class="comment-time">{{ formatCommentTime(comment.created_at) }}</span>
          </div>
        </div>

        <!-- 评论内容 -->
        <div class="comment-content">
          {{ comment.content }}
        </div>

        <!-- 评论操作 -->
        <div class="comment-actions">
          <button
            @click="handleReply"
            class="action-btn reply-btn"
          >
            <span class="action-icon">💬</span>
            <span>回复</span>
          </button>

          <!-- 回复数量和展开/收起按钮 -->
          <button
            v-if="hasReplies"
            @click="toggleReplies"
            class="action-btn toggle-btn"
          >
            <span class="toggle-text">{{ showReplies ? '收起' : '展开' }}{{ replyCount }}条回复</span>
            <el-icon class="toggle-icon" :class="{ 'rotated': showReplies }">
              <ArrowDown />
            </el-icon>
          </button>

          <button
            v-if="canDelete"
            @click="handleDelete"
            class="action-btn delete-btn"
          >
            <span class="action-icon">🗑️</span>
            <span>删除</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 回复列表 -->
    <div v-if="hasReplies && showReplies" class="replies-section">
      <div class="replies-bg"></div>
      <div class="replies-list">
        <div
          v-for="reply in comment.replies"
          :key="reply.id"
          class="reply-item"
        >
          <div class="reply-avatar">
            <div class="avatar-circle small">👤</div>
          </div>

          <div class="reply-content-wrapper">
            <!-- 回复头部 -->
            <div class="reply-header">
              <div class="user-info">
                <span class="user-name">{{ getUserDisplayName(reply.user) }}</span>
                <span v-if="isDocumentAuthor(reply.user.id)" class="author-badge">作者</span>
                <span class="reply-time">{{ formatCommentTime(reply.created_at) }}</span>
              </div>
            </div>

            <!-- 回复内容 -->
            <div class="reply-content">
              {{ reply.content }}
            </div>

            <!-- 回复操作 -->
            <div class="reply-actions">
              <button
                v-if="canDeleteReply(reply)"
                @click="handleDeleteReply(reply)"
                class="action-btn delete-btn small"
              >
                <span class="action-icon">🗑️</span>
                <span>删除</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { canDeleteComment } from '@/api/v2/interaction'

// ==================== Props ====================
const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  documentAuthorId: {
    type: [Number, String],
    default: null
  }
})

// ==================== Emits ====================
const emit = defineEmits(['reply', 'delete', 'login-required'])

// ==================== 响应式数据 ====================
const userStore = useUserStore()
const showReplies = ref(false)

// ==================== 计算属性 ====================
const isLoggedIn = computed(() => !!userStore.token)

const canDelete = computed(() => {
  if (!isLoggedIn.value || !userStore.userInfo) return false

  return canDeleteComment(
    props.comment,
    userStore.userInfo,
    { author_id: props.documentAuthorId }
  )
})

const hasReplies = computed(() => {
  return props.comment.replies && props.comment.replies.length > 0
})

const replyCount = computed(() => {
  return props.comment.reply_count || (props.comment.replies ? props.comment.replies.length : 0)
})

// ==================== 方法 ====================

/**
 * 获取用户显示名称
 */
const getUserDisplayName = (user) => {
  if (!user) return '未知用户'
  return user.nickname || user.username || `用户${user.id}`
}

/**
 * 判断是否为文档作者
 */
const isDocumentAuthor = (userId) => {
  return props.documentAuthorId && userId == props.documentAuthorId
}

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
 * 检查是否可以删除回复
 */
const canDeleteReply = (reply) => {
  if (!isLoggedIn.value || !userStore.userInfo) return false

  return canDeleteComment(
    reply,
    userStore.userInfo,
    { author_id: props.documentAuthorId }
  )
}

/**
 * 切换回复展开/收起
 */
const toggleReplies = () => {
  showReplies.value = !showReplies.value
}

/**
 * 处理回复
 */
const handleReply = () => {
  if (!isLoggedIn.value) {
    emit('login-required')
    return
  }

  emit('reply', props.comment)
}

/**
 * 处理删除评论
 */
const handleDelete = () => {
  emit('delete', props.comment, false, null)
}

/**
 * 处理删除回复
 */
const handleDeleteReply = (reply) => {
  emit('delete', reply, true, props.comment)
}
</script>

<style scoped>
.comment-item {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  margin-bottom: 16px;
}

.comment-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.comment-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #ffeaa7, #fd79a8);
  background-size: 400% 400%;
  border-radius: 22px;
  z-index: -1;
  animation: gradientShift 8s ease infinite;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.comment-item:hover .comment-glow {
  opacity: 0.4;
}

/* 主评论 */
.comment-main {
  padding: 24px;
  display: flex;
  gap: 16px;
}

.comment-avatar {
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
  font-size: 18px;
  color: white;
  box-shadow: 0 4px 12px rgba(255, 154, 158, 0.4);
}

.avatar-circle.small {
  width: 36px;
  height: 36px;
  font-size: 16px;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  box-shadow: 0 3px 10px rgba(168, 237, 234, 0.4);
}

.comment-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.author-badge {
  background: linear-gradient(135deg, #ffeaa7 0%, #fd79a8 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 6px rgba(255, 234, 167, 0.4);
}

.comment-time {
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
}

.comment-content {
  color: #374151;
  font-size: 15px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.comment-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 4px;
}

.action-btn {
  padding: 6px 12px;
  font-size: 13px;
  border-radius: 20px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  border: 2px solid transparent;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
}

.action-btn.small {
  padding: 4px 10px;
  font-size: 12px;
}

.action-icon {
  font-size: 14px;
}

.reply-btn {
  color: #4ecdc4;
  background: rgba(78, 205, 196, 0.1);
  border-color: rgba(78, 205, 196, 0.2);
}

.reply-btn:hover {
  background: rgba(78, 205, 196, 0.2);
  border-color: rgba(78, 205, 196, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.delete-btn {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  border-color: rgba(255, 107, 107, 0.2);
}

.delete-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.toggle-btn {
  color: #fd79a8;
  background: rgba(253, 121, 168, 0.1);
  border-color: rgba(253, 121, 168, 0.2);
  font-weight: 600;
}

.toggle-btn:hover {
  background: rgba(253, 121, 168, 0.2);
  border-color: rgba(253, 121, 168, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(253, 121, 168, 0.3);
}

.toggle-text {
  font-size: 13px;
}

.toggle-icon {
  font-size: 12px;
  transition: transform 0.3s ease;
  margin-left: 4px;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

/* 回复区域 */
.replies-section {
  border-top: 2px solid rgba(255, 154, 158, 0.1);
  position: relative;
  overflow: hidden;
  animation: slideDown 0.4s ease;
}

.replies-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(168, 237, 234, 0.1) 0%, rgba(254, 214, 227, 0.1) 100%);
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 2000px;
  }
}

.replies-list {
  padding: 20px 24px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.reply-item {
  display: flex;
  gap: 12px;
  position: relative;
  padding-left: 20px;
}

.reply-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  border-radius: 2px;
}

.reply-avatar {
  flex-shrink: 0;
}

.reply-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.reply-time {
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
}

.reply-content {
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.reply-actions {
  display: flex;
  gap: 4px;
  align-items: center;
  margin-top: 4px;
}

/* 响应式 */
@media (max-width: 768px) {
  .comment-main {
    padding: 20px;
    gap: 12px;
  }

  .avatar-circle {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }

  .avatar-circle.small {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .comment-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .user-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .comment-actions {
    flex-wrap: wrap;
    gap: 6px;
  }

  .replies-list {
    padding: 16px 20px 20px 20px;
    gap: 12px;
  }

  .reply-item {
    gap: 10px;
    padding-left: 16px;
  }

  .action-btn {
    font-size: 12px;
    padding: 5px 10px;
  }

  .toggle-text {
    font-size: 12px;
  }
}
</style>
