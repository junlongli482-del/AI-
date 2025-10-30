/**
 * 互动功能模块 API - 修复版
 */
import request from '@/utils/request'

// ==================== 点赞功能 ====================

/**
 * 切换点赞状态
 */
export const toggleLike = (documentId) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/like`,
    method: 'post'
  })
}

/**
 * 获取点赞状态（公开接口）
 */
export const getLikeStatus = (documentId) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/like-status`,
    method: 'get'
  })
}

// ==================== 收藏功能 ====================

/**
 * 切换收藏状态
 */
export const toggleFavorite = (documentId) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/favorite`,
    method: 'post'
  })
}

/**
 * 获取收藏状态（公开接口）
 */
export const getFavoriteStatus = (documentId) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/favorite-status`,
    method: 'get'
  })
}

/**
 * 获取我的收藏列表
 */
export const getMyFavorites = (params = {}) => {
  return request({
    url: '/v2/interaction/my-favorites',
    method: 'get',
    params: {
      page: 1,
      size: 20,
      ...params
    }
  })
}

// ==================== 评论功能 ====================

/**
 * 创建评论或回复
 */
export const createComment = (documentId, data) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/comments`,
    method: 'post',
    data
  })
}

/**
 * 获取评论列表（公开接口）
 */
export const getComments = (documentId, params = {}) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/comments`,
    method: 'get',
    params: {
      page: 1,
      size: 20,
      ...params
    }
  })
}

/**
 * 更新评论内容
 */
export const updateComment = (commentId, data) => {
  return request({
    url: `/v2/interaction/comments/${commentId}`,
    method: 'put',
    data
  })
}

/**
 * 删除评论
 */
export const deleteComment = (commentId) => {
  return request({
    url: `/v2/interaction/comments/${commentId}`,
    method: 'delete'
  })
}

// ==================== 统计功能 ====================

/**
 * 获取文档互动统计（公开接口）
 */
export const getDocumentStats = (documentId) => {
  return request({
    url: `/v2/interaction/documents/${documentId}/stats`,
    method: 'get'
  })
}

/**
 * 获取我的互动统计
 */
export const getMyStats = () => {
  return request({
    url: '/v2/interaction/my-stats',
    method: 'get'
  })
}

// ==================== 🔥 新增：批量获取文档状态 ====================

/**
 * 批量获取文档的个人互动状态
 * @param {Array} documentIds - 文档ID数组
 * @returns {Promise} 返回每个文档的个人状态
 */
export const getBatchInteractionStatus = (documentIds) => {
  if (!documentIds || documentIds.length === 0) {
    return Promise.resolve({})
  }

  return Promise.all(
    documentIds.map(async (docId) => {
      try {
        const [likeStatus, favoriteStatus] = await Promise.all([
          getLikeStatus(docId),
          getFavoriteStatus(docId)
        ])

        return {
          documentId: docId,
          is_liked: likeStatus.is_liked,
          is_favorited: favoriteStatus.is_favorited,
          like_count: likeStatus.like_count,
          favorite_count: favoriteStatus.favorite_count
        }
      } catch (error) {
        console.warn(`获取文档${docId}状态失败:`, error)
        return {
          documentId: docId,
          is_liked: false,
          is_favorited: false,
          like_count: 0,
          favorite_count: 0
        }
      }
    })
  ).then(results => {
    // 转换为以documentId为key的对象
    const statusMap = {}
    results.forEach(item => {
      statusMap[item.documentId] = item
    })
    return statusMap
  })
}

// ==================== 🔥 新增：全局状态管理 ====================

/**
 * 互动状态缓存
 */
const interactionCache = new Map()

/**
 * 更新缓存中的文档状态
 */
export const updateDocumentCache = (documentId, updates) => {
  const current = interactionCache.get(documentId) || {}
  const updated = { ...current, ...updates }
  interactionCache.set(documentId, updated)

  // 触发全局事件，通知其他组件更新
  window.dispatchEvent(new CustomEvent('documentInteractionUpdate', {
    detail: { documentId, data: updated }
  }))
}

/**
 * 获取缓存中的文档状态
 */
export const getDocumentCache = (documentId) => {
  return interactionCache.get(documentId) || null
}

/**
 * 清空缓存（用户登录/退出时调用）
 */
export const clearInteractionCache = () => {
  interactionCache.clear()
}

// ==================== 工具函数 ====================

/**
 * 格式化互动数量显示
 */
export const formatInteractionCount = (count) => {
  if (!count || count === 0) return '0'

  if (count < 1000) {
    return count.toString()
  } else if (count < 10000) {
    return (count / 1000).toFixed(1) + 'k'
  } else if (count < 100000000) {
    return (count / 10000).toFixed(1) + 'w'
  } else {
    return '99w+'
  }
}

/**
 * 检查是否可以删除评论
 */
export const canDeleteComment = (comment, currentUser, document) => {
  if (!currentUser || !comment) return false

  const isCommentAuthor = comment.user.id === currentUser.id
  const isDocumentAuthor = document && document.author_id === currentUser.id

  return isCommentAuthor || isDocumentAuthor
}

/**
 * 验证评论内容
 */
export const validateCommentContent = (content) => {
  if (!content || !content.trim()) {
    return { valid: false, message: '评论内容不能为空' }
  }

  if (content.trim().length < 2) {
    return { valid: false, message: '评论内容至少需要2个字符' }
  }

  if (content.length > 1000) {
    return { valid: false, message: '评论内容不能超过1000个字符' }
  }

  return { valid: true, message: '' }
}

// ==================== 枚举常量 ====================

export const InteractionTypes = {
  LIKE: 'like',
  FAVORITE: 'favorite',
  COMMENT: 'comment'
}

export const CommentTypes = {
  COMMENT: 'comment',
  REPLY: 'reply'
}

export const InteractionTexts = {
  [InteractionTypes.LIKE]: {
    active: '已点赞',
    inactive: '点赞'
  },
  [InteractionTypes.FAVORITE]: {
    active: '已收藏',
    inactive: '收藏'
  }
}

// 默认导出
export default {
  toggleLike,
  getLikeStatus,
  toggleFavorite,
  getFavoriteStatus,
  getMyFavorites,
  createComment,
  getComments,
  updateComment,
  deleteComment,
  getDocumentStats,
  getMyStats,
  getBatchInteractionStatus,
  updateDocumentCache,
  getDocumentCache,
  clearInteractionCache,
  formatInteractionCount,
  canDeleteComment,
  validateCommentContent,
  InteractionTypes,
  CommentTypes,
  InteractionTexts
}
