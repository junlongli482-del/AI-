<template>
  <div class="publish-status-container">
    <!-- 状态标签 + 图标 -->
    <div class="status-display" @click.stop="handleStatusClick">
      <el-tag
        :type="statusConfig.type"
        size="small"
        class="status-tag"
        :class="{ 'clickable': hasDetail }"
      >
        <span class="status-icon">{{ statusConfig.icon }}</span>
        <span class="status-text">{{ statusConfig.text }}</span>
      </el-tag>

      <!-- 单个文档刷新按钮（仅审核中状态显示） -->
      <el-button
        v-if="showRefreshButton"
        type="text"
        size="small"
        class="refresh-btn"
        :loading="refreshing"
        @click.stop="handleRefresh"
        title="刷新状态"
      >
        <el-icon><Refresh /></el-icon>
      </el-button>
    </div>

    <!-- 审核详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="审核详情"
      width="600px"
      :close-on-click-modal="false"
      append-to-body
    >
      <div v-if="reviewDetail" class="review-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>审核信息</h4>
          <div class="detail-item">
            <span class="label">审核类型：</span>
            <span class="value">{{ reviewDetail.review_type || '内容安全审核' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">审核结果：</span>
            <el-tag :type="getReviewStatusType(reviewDetail.review_result)" size="small">
              {{ getReviewStatusText(reviewDetail.review_result) }}
            </el-tag>
          </div>
          <div class="detail-item">
            <span class="label">审核时长：</span>
            <span class="value">{{ formatReviewDuration(reviewDetail.review_duration) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">审核时间：</span>
            <span class="value">{{ formatDateTime(reviewDetail.created_at) }}</span>
          </div>
        </div>

        <!-- 失败原因（如果有） -->
        <div v-if="reviewDetail.failure_reason" class="detail-section">
          <h4>失败原因</h4>
          <div class="failure-reason">
            {{ reviewDetail.failure_reason }}
          </div>
        </div>

        <!-- 置信度（如果有） -->
        <div v-if="reviewDetail.confidence_score" class="detail-section">
          <h4>审核置信度</h4>
          <div class="confidence-score">
            <el-progress
              :percentage="Math.round(reviewDetail.confidence_score * 100)"
              :color="getConfidenceColor(reviewDetail.confidence_score)"
            />
            <span class="score-text">{{ (reviewDetail.confidence_score * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>

      <div v-else class="loading-detail">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载审核详情中...</span>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button
            v-if="canRetryReview(document.status)"
            type="primary"
            @click="handleRetryReview"
            :loading="retrying"
          >
            重新审核
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Loading } from '@element-plus/icons-vue'
import {
  getReviewStatus,
  retryReview,
  getReviewStatusText,
  getReviewStatusType,
  canRetryReview,
  formatReviewDuration
} from '@/api/v2/ai_review/index'

const props = defineProps({
  document: {
    type: Object,
    required: true
  },
  // 是否显示刷新按钮
  showRefresh: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['status-updated', 'retry-review'])

// 响应式数据
const refreshing = ref(false)
const detailDialogVisible = ref(false)
const reviewDetail = ref(null)
const retrying = ref(false)

// 计算属性：状态配置
const statusConfig = computed(() => {
  const status = props.document.status

  // 🆕 判断是否为更新发布失败
  const isUpdateFailed = status === 'review_failed' && props.document.publish_time

  // 根据文档状态返回对应的显示配置
  const configs = {
    draft: {
      text: '草稿',
      icon: '📝',
      type: 'info',
      color: '#909399'
    },
    pending_review: {
      text: '审核中',
      icon: '⏳',
      type: 'warning',
      color: '#E6A23C'
    },
    published: {
      text: '已发布',
      icon: '✅',
      type: 'success',
      color: '#67C23A'
    },
    review_failed: {
      text: '审核失败',
      icon: '❌',
      type: 'danger',
      color: '#F56C6C'
    },
    // 🆕 新增更新发布失败状态
    update_failed: {
      text: '更新失败',
      icon: '⚠️',
      type: 'warning',
      color: '#E6A23C'
    }
  }

  // 🆕 如果是更新发布失败，返回特殊状态
  if (isUpdateFailed) {
    return configs.update_failed
  }

  return configs[status] || configs.draft
})

// 计算属性：是否显示刷新按钮
const showRefreshButton = computed(() => {
  return props.showRefresh &&
    props.document.status === 'pending_review'
})

// 计算属性：是否有详情可查看
const hasDetail = computed(() => {
  const status = props.document.status
  const isUpdateFailed = status === 'review_failed' && props.document.publish_time

  // 审核失败或更新失败都可以查看详情
  return status === 'review_failed' || isUpdateFailed
})

// 处理状态点击
const handleStatusClick = async () => {
  if (!hasDetail.value) return

  // 如果是审核失败状态，显示审核详情
  if (props.document.status === 'review_failed') {
    await loadReviewDetail()
    detailDialogVisible.value = true
  }
}

// 处理刷新状态
const handleRefresh = async () => {
  refreshing.value = true

  try {
    // 查询最新的审核状态
    const statusData = await getReviewStatus(props.document.id)

    // 根据审核状态更新文档状态
    let newStatus = props.document.status
    if (statusData.overall_status === 'passed') {
      newStatus = 'published'
    } else if (statusData.overall_status === 'failed') {
      newStatus = 'review_failed'
    }

    // 触发状态更新事件
    if (newStatus !== props.document.status) {
      emit('status-updated', {
        documentId: props.document.id,
        oldStatus: props.document.status,
        newStatus: newStatus,
        statusData: statusData
      })

      ElMessage.success('状态已更新')
    } else {
      ElMessage.info('状态无变化')
    }

  } catch (error) {
    console.error('刷新状态失败:', error)
    ElMessage.error('刷新状态失败')
  } finally {
    refreshing.value = false
  }
}

// 加载审核详情
const loadReviewDetail = async () => {
  try {
    const statusData = await getReviewStatus(props.document.id)

    if (statusData.review_logs && statusData.review_logs.length > 0) {
      // 获取最新的审核记录
      const latestReview = statusData.review_logs[statusData.review_logs.length - 1]
      reviewDetail.value = latestReview
    }
  } catch (error) {
    console.error('加载审核详情失败:', error)
    ElMessage.error('加载审核详情失败')
  }
}

// 处理重新审核
const handleRetryReview = async () => {
  retrying.value = true

  try {
    await retryReview(props.document.id)

    // 触发重新审核事件
    emit('retry-review', {
      documentId: props.document.id,
      oldStatus: props.document.status,
      newStatus: 'pending_review'
    })

    ElMessage.success('已重新提交审核')
    detailDialogVisible.value = false

  } catch (error) {
    console.error('重新审核失败:', error)
    ElMessage.error('重新审核失败')
  } finally {
    retrying.value = false
  }
}

// 获取置信度颜色
const getConfidenceColor = (score) => {
  if (score >= 0.8) return '#67C23A'
  if (score >= 0.6) return '#E6A23C'
  return '#F56C6C'
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 监听文档变化，清理详情数据
watch(() => props.document.id, () => {
  reviewDetail.value = null
  detailDialogVisible.value = false
})
</script>

<style scoped>
.publish-status-container {
  display: inline-block;
}

.status-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: default;
  transition: all 0.2s ease;
}

.status-tag.clickable {
  cursor: pointer;
}

.status-tag.clickable:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 12px;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
}

.refresh-btn {
  padding: 4px;
  min-height: auto;
  color: #909399;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  color: #007AFF;
  background: rgba(0, 122, 255, 0.1);
}

.refresh-btn .el-icon {
  font-size: 14px;
}

/* 对话框样式 */
.review-detail {
  max-height: 500px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
  border-bottom: 1px solid #d0d7de;
  padding-bottom: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .label {
  width: 100px;
  color: #656d76;
  flex-shrink: 0;
}

.detail-item .value {
  color: #24292f;
  flex: 1;
}

.failure-reason {
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 6px;
  padding: 12px;
  color: #f56c6c;
  font-size: 14px;
  line-height: 1.5;
}

.confidence-score {
  display: flex;
  align-items: center;
  gap: 12px;
}

.confidence-score .el-progress {
  flex: 1;
}

.score-text {
  font-size: 14px;
  font-weight: 600;
  color: #24292f;
  min-width: 50px;
}

.loading-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 12px;
  color: #656d76;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 滚动条样式 */
.review-detail::-webkit-scrollbar {
  width: 6px;
}

.review-detail::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.review-detail::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}
</style>
