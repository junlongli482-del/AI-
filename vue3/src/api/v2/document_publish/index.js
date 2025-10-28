import request from '@/utils/request'

/**
 * 文档发布模块API
 * 基础路径: /api/v2/document_publish
 */

// ==================== 发布管理 ====================

/**
 * 提交发布申请
 * @param {Object} data - 发布数据
 * @param {number} data.document_id - 文档ID
 * @param {string} data.publish_reason - 发布说明（可选）
 * @param {Object} data.publish_config - 发布配置（可选）
 * @returns {Promise} 发布记录
 */
export const submitPublish = (data) => {
  return request({
    url: `/v2/document_publish/submit`,
    method: 'post',
    data
  })
}

/**
 * 撤回已发布文档
 * @param {number} documentId - 文档ID
 * @param {string} reason - 撤回原因
 * @returns {Promise} 发布记录
 */
export const unpublishDocument = (documentId, reason = '') => {
  return request({
    url: `/v2/document_publish/unpublish/${documentId}`,
    method: 'post',
    data: { unpublish_reason: reason }
  })
}

/**
 * 获取发布状态
 * @param {number} documentId - 文档ID
 * @returns {Promise} 发布状态
 */
export const getPublishStatus = (documentId) => {
  return request({
    url: `/v2/document_publish/status/${documentId}`,
    method: 'get'
  })
}

/**
 * 获取发布详情
 * @param {number} documentId - 文档ID
 * @returns {Promise} 发布详情
 */
export const getPublishDetail = (documentId) => {
  return request({
    url: `/v2/document_publish/document/${documentId}`,
    method: 'get'
  })
}

// ==================== 文档展示（公开接口） ====================

/**
 * 获取已发布文档列表（公开接口）
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @param {string} params.status - 发布状态筛选
 * @param {boolean} params.is_featured - 是否精选筛选
 * @returns {Promise} 分页的已发布文档
 */
export const getPublishedDocuments = (params = {}) => {
  return request({
    url: `/v2/document_publish/published`,
    method: 'get',
    params: {
      page: 1,
      size: 20,
      ...params
    }
  })
}

/**
 * 增加文档浏览量（公开接口）
 * @param {number} documentId - 文档ID
 * @returns {Promise} 操作结果
 */
export const incrementViewCount = (documentId) => {
  return request({
    url: `/v2/document_publish/view/${documentId}`,
    method: 'post'
  })
}

// ==================== 个人管理 ====================

/**
 * 获取我的发布记录
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页数量
 * @returns {Promise} 分页的发布记录
 */
export const getMyPublishRecords = (params = {}) => {
  return request({
    url: `/v2/document_publish/my-records`,
    method: 'get',
    params: {
      page: 1,
      size: 20,
      ...params
    }
  })
}

/**
 * 获取发布统计信息
 * @param {boolean} globalStats - 是否获取全局统计
 * @returns {Promise} 发布统计数据
 */
export const getPublishStats = (globalStats = false) => {
  return request({
    url: `/v2/document_publish/stats`,
    method: 'get',
    params: { global_stats: globalStats }
  })
}

// ==================== 配置信息 ====================

/**
 * 获取发布配置信息
 * @returns {Promise} 发布配置
 */
export const getPublishConfig = () => {
  return request({
    url: `/v2/document_publish/config`,
    method: 'get'
  })
}

// ==================== 工具函数 ====================

/**
 * 发布状态枚举
 */
export const PublishStatus = {
  DRAFT: 'draft',
  PENDING_REVIEW: 'pending_review',
  REVIEW_PASSED: 'review_passed',
  REVIEW_FAILED: 'review_failed',
  PUBLISHED: 'published',
  UNPUBLISHED: 'unpublished'
}

/**
 * 发布状态文本映射
 */
export const PublishStatusText = {
  [PublishStatus.DRAFT]: '草稿',
  [PublishStatus.PENDING_REVIEW]: '待审核',
  [PublishStatus.REVIEW_PASSED]: '审核通过',
  [PublishStatus.REVIEW_FAILED]: '审核失败',
  [PublishStatus.PUBLISHED]: '已发布',
  [PublishStatus.UNPUBLISHED]: '已撤回'
}

/**
 * 获取发布状态显示文本
 * @param {string} status - 发布状态
 * @returns {string} 显示文本
 */
export const getPublishStatusText = (status) => {
  return PublishStatusText[status] || status
}

/**
 * 获取发布状态类型（用于Element Plus标签）
 * @param {string} status - 发布状态
 * @returns {string} Element Plus标签类型
 */
export const getPublishStatusType = (status) => {
  const typeMap = {
    [PublishStatus.DRAFT]: 'info',
    [PublishStatus.PENDING_REVIEW]: 'warning',
    [PublishStatus.REVIEW_PASSED]: 'success',
    [PublishStatus.REVIEW_FAILED]: 'danger',
    [PublishStatus.PUBLISHED]: 'success',
    [PublishStatus.UNPUBLISHED]: 'info'
  }
  return typeMap[status] || 'info'
}

/**
 * 检查是否可以发布
 * @param {string} status - 文档状态
 * @returns {boolean} 是否可以发布
 */
export const canPublish = (status) => {
  return [PublishStatus.DRAFT, PublishStatus.UNPUBLISHED].includes(status)
}

/**
 * 检查是否可以撤回发布
 * @param {string} status - 发布状态
 * @returns {boolean} 是否可以撤回
 */
export const canUnpublish = (status) => {
  return status === PublishStatus.PUBLISHED
}

/**
 * 检查是否可以更新发布
 * @param {string} status - 发布状态
 * @param {boolean} isModified - 文档是否已修改
 * @returns {boolean} 是否可以更新发布
 */
export const canUpdatePublish = (status, isModified = false) => {
  return status === PublishStatus.PUBLISHED && isModified
}

/**
 * 格式化浏览量
 * @param {number} viewCount - 浏览量
 * @returns {string} 格式化后的浏览量
 */
export const formatViewCount = (viewCount) => {
  if (!viewCount || viewCount === 0) return '0'

  if (viewCount < 1000) {
    return viewCount.toString()
  } else if (viewCount < 10000) {
    return `${(viewCount / 1000).toFixed(1)}k`
  } else if (viewCount < 100000) {
    return `${Math.floor(viewCount / 1000)}k`
  } else {
    return `${(viewCount / 10000).toFixed(1)}w`
  }
}

/**
 * 生成默认发布说明
 * @param {string} title - 文档标题
 * @returns {string} 默认发布说明
 */
export const generateDefaultPublishReason = (title) => {
  return `分享文档：${title}`
}

/**
 * 验证发布数据
 * @param {Object} data - 发布数据
 * @returns {Object} 验证结果 { valid: boolean, message: string }
 */
export const validatePublishData = (data) => {
  if (!data.document_id) {
    return { valid: false, message: '文档ID不能为空' }
  }

  if (data.publish_reason && data.publish_reason.length > 200) {
    return { valid: false, message: '发布说明不能超过200字符' }
  }

  return { valid: true, message: '' }
}

/**
 * 更新已发布文档
 * @param {number} documentId - 文档ID
 * @param {Object} data - 更新数据
 * @param {string} data.title - 新标题（可选）
 * @param {string} data.content - 新内容（可选）
 * @param {string} data.summary - 新摘要（可选）
 * @param {string} data.update_reason - 更新原因（必填）
 * @returns {Promise} 更新结果
 */
export const updatePublishedDocument = (documentId, data) => {
  return request({
    url: `/v2/document_publish/update/${documentId}`,
    method: 'put',
    data
  })
}
