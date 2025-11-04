import request from '@/utils/request'

/**
 * AI审核模块API
 * 基础路径: /api/v2/ai_review
 */

// ==================== 审核管理 ====================

/**
 * 提交文档审核
 * @param {number} documentId - 文档ID
 * @returns {Promise} 审核记录
 */
export const submitReview = (documentId) => {
  return request({
    url: `/v2/ai_review/submit-review`,
    method: 'post',
    params: { document_id: documentId }
  })
}

/**
 * 查询审核状态
 * @param {number} documentId - 文档ID
 * @returns {Promise} 审核状态详情
 */
export const getReviewStatus = (documentId) => {
  return request({
    url: `/v2/ai_review/review-status/${documentId}`,
    method: 'get'
  })
}

/**
 * 重新审核文档
 * @param {number} documentId - 文档ID
 * @returns {Promise} 审核记录
 */
export const retryReview = (documentId) => {
  return request({
    url: `/v2/ai_review/retry-review/${documentId}`,
    method: 'post'
  })
}

/**
 * 获取审核详情
 * @param {number} reviewId - 审核记录ID
 * @returns {Promise} 审核详情
 */
export const getReviewDetail = (reviewId) => {
  return request({
    url: `/v2/ai_review/review-detail/${reviewId}`,
    method: 'get'
  })
}

// ==================== 历史统计 ====================

/**
 * 获取审核历史记录
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @param {string} params.review_result - 筛选结果 (pending/passed/failed/error)
 * @returns {Promise} 分页的审核历史
 */
export const getReviewHistory = (params = {}) => {
  return request({
    url: `/v2/ai_review/review-history`,
    method: 'get',
    params: {
      page: 1,
      size: 20,
      ...params
    }
  })
}

/**
 * 获取审核统计信息
 * @returns {Promise} 审核统计数据
 */
export const getReviewStats = () => {
  return request({
    url: `/v2/ai_review/stats`,
    method: 'get'
  })
}

/**
 * 获取最近审核记录
 * @param {number} limit - 返回数量 (1-50)
 * @returns {Promise} 最近审核记录
 */
export const getRecentReviews = (limit = 10) => {
  return request({
    url: `/v2/ai_review/recent-reviews`,
    method: 'get',
    params: { limit }
  })
}

// ==================== 配置管理 ====================

/**
 * 获取审核配置信息
 * @returns {Promise} 审核配置
 */
export const getReviewConfig = () => {
  return request({
    url: `/v2/ai_review/config`,
    method: 'get'
  })
}

// ==================== 工具函数 ====================

/**
 * 审核结果状态映射
 */
export const ReviewStatus = {
  PENDING: 'pending',
  PASSED: 'passed',
  FAILED: 'failed',
  ERROR: 'error'
}

/**
 * 审核结果状态文本
 */
export const ReviewStatusText = {
  [ReviewStatus.PENDING]: '审核中',
  [ReviewStatus.PASSED]: '审核通过',
  [ReviewStatus.FAILED]: '审核失败',
  [ReviewStatus.ERROR]: '审核出错'
}

/**
 * 获取审核状态显示文本
 * @param {string} status - 审核状态
 * @returns {string} 显示文本
 */
export const getReviewStatusText = (status) => {
  return ReviewStatusText[status] || status
}

/**
 * 获取审核状态类型（用于Element Plus标签）
 * @param {string} status - 审核状态
 * @returns {string} Element Plus标签类型
 */
export const getReviewStatusType = (status) => {
  const typeMap = {
    [ReviewStatus.PENDING]: 'warning',
    [ReviewStatus.PASSED]: 'success',
    [ReviewStatus.FAILED]: 'danger',
    [ReviewStatus.ERROR]: 'danger'
  }
  return typeMap[status] || 'info'
}

/**
 * 检查是否可以重新审核
 * @param {string} status - 审核状态
 * @returns {boolean} 是否可以重新审核
 */
export const canRetryReview = (status) => {
  return [ReviewStatus.FAILED, ReviewStatus.ERROR].includes(status)
}

/**
 * 格式化审核时长
 * @param {number} duration - 审核时长（秒）
 * @returns {string} 格式化后的时长
 */
export const formatReviewDuration = (duration) => {
  if (!duration) return '-'

  if (duration < 60) {
    return `${duration}秒`
  } else if (duration < 3600) {
    return `${Math.floor(duration / 60)}分${duration % 60}秒`
  } else {
    const hours = Math.floor(duration / 3600)
    const minutes = Math.floor((duration % 3600) / 60)
    return `${hours}小时${minutes}分钟`
  }
}

/**
 * 验证审核失败原因是否需要显示详情
 * @param {string} reason - 失败原因
 * @returns {boolean} 是否需要显示详情
 */
export const shouldShowReviewDetail = (reason) => {
  return reason && reason.length > 50
}

/**
 * 🆕 直接内容审核
 * @param {Object} data - 审核数据
 * @param {string} data.title - 文档标题
 * @param {string} data.content - 文档内容
 * @param {number} data.document_id - 文档ID（可选）
 * @returns {Promise} 审核结果
 * @example
 * const result = await contentReview({
 *   title: '文档标题',
 *   content: '# 文档内容\n\n...',
 *   document_id: 123
 * })
 * if (result.review_result === 'passed') {
 *   // 审核通过
 * } else {
 *   // 审核失败，显示 result.failure_reason
 * }
 */
export const contentReview = (data) => {
  return request({
    url: `/v2/ai_review/content-review`,
    method: 'post',
    data: {
      title: data.title,
      content: data.content,
      document_id: data.document_id || null
    }
  })
}
