import request from '@/utils/request'

// ==================== 基础接口 ====================

/**
 * 模块测试
 */
export const testModule = () => {
  return request({
    url: '/v2/tech_square/test',
    method: 'get'
  })
}

/**
 * 获取文档列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码（默认1）
 * @param {number} params.size - 每页数量（默认20）
 * @param {string} params.search - 搜索关键词（可选）
 * @param {string} params.file_type - 文件类型（可选：md、pdf）
 * @param {string} params.time_filter - 时间筛选（可选：today、week、month）
 * @param {string} params.sort_by - 排序方式（可选：latest、popular、recommended）
 */
export const getDocuments = (params = {}) => {
  return request({
    url: '/v2/tech_square/documents',
    method: 'get',
    params: {
      page: 1,
      size: 20,
      sort_by: 'latest',
      ...params
    }
  })
}

/**
 * 获取文档详情
 * @param {number} documentId - 文档ID
 */
export const getDocumentDetail = (documentId) => {
  return request({
    url: `/v2/tech_square/documents/${documentId}`,
    method: 'get'
  })
}

/**
 * 搜索文档
 * @param {Object} params - 搜索参数
 * @param {string} params.keyword - 搜索关键词（必填）
 * @param {number} params.page - 页码（默认1）
 * @param {number} params.size - 每页数量（默认20）
 * @param {string} params.file_type - 文件类型筛选（可选）
 */
export const searchDocuments = (params) => {
  return request({
    url: '/v2/tech_square/search',
    method: 'get',
    params: {
      page: 1,
      size: 20,
      ...params
    }
  })
}

/**
 * 获取分类统计
 */
export const getCategoryStats = () => {
  return request({
    url: '/v2/tech_square/category-stats',
    method: 'get'
  })
}

/**
 * 获取热门文档
 * @param {number} limit - 返回数量（默认10）
 */
export const getHotDocuments = (limit = 10) => {
  return request({
    url: '/v2/tech_square/hot-documents',
    method: 'get',
    params: { limit }
  })
}

/**
 * 获取最新文档
 * @param {number} limit - 返回数量（默认10）
 */
export const getLatestDocuments = (limit = 10) => {
  return request({
    url: '/v2/tech_square/latest-documents',
    method: 'get',
    params: { limit }
  })
}

/**
 * 获取统计信息
 */
export const getStats = () => {
  return request({
    url: '/v2/tech_square/stats',
    method: 'get'
  })
}

/**
 * 增加浏览量
 * @param {number} documentId - 文档ID
 */
export const incrementViewCount = (documentId) => {
  return request({
    url: `/v2/tech_square/view/${documentId}`,
    method: 'post'
  })
}

// ==================== 工具函数 ====================

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小
 */
export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化时间显示
 * @param {string} dateString - 时间字符串
 * @returns {string} 格式化后的时间
 */
export const formatTime = (dateString) => {
  if (!dateString) return ''

  const now = new Date()
  const date = new Date(dateString)
  const diff = now - date

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < week) {
    return `${Math.floor(diff / day)}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

/**
 * 格式化浏览量显示
 * @param {number} count - 浏览量
 * @returns {string} 格式化后的浏览量
 */
export const formatViewCount = (count) => {
  if (!count) return '0'

  if (count < 1000) {
    return count.toString()
  } else if (count < 10000) {
    return (count / 1000).toFixed(1) + 'k'
  } else {
    return (count / 10000).toFixed(1) + 'w'
  }
}

/**
 * 获取文件类型图标
 * @param {string} fileType - 文件类型
 * @returns {string} 图标
 */
export const getFileTypeIcon = (fileType) => {
  const icons = {
    md: '📝',
    pdf: '📄'
  }
  return icons[fileType] || '📄'
}

/**
 * 获取文件类型文本
 * @param {string} fileType - 文件类型
 * @returns {string} 类型文本
 */
export const getFileTypeText = (fileType) => {
  const texts = {
    md: 'Markdown',
    pdf: 'PDF文档'
  }
  return texts[fileType] || '未知类型'
}

// ==================== 枚举常量 ====================

/**
 * 排序方式
 */
export const SortTypes = {
  LATEST: 'latest',
  POPULAR: 'popular',
  RECOMMENDED: 'recommended'
}

/**
 * 排序方式显示文本
 */
export const SortTypeTexts = {
  [SortTypes.LATEST]: '最新发布',
  [SortTypes.POPULAR]: '最受欢迎',
  [SortTypes.RECOMMENDED]: '智能推荐'
}

/**
 * 文件类型
 */
export const FileTypes = {
  MD: 'md',
  PDF: 'pdf'
}

/**
 * 文件类型显示文本
 */
export const FileTypeTexts = {
  [FileTypes.MD]: 'MD文档',
  [FileTypes.PDF]: 'PDF文档'
}

/**
 * 时间筛选
 */
export const TimeFilters = {
  TODAY: 'today',
  WEEK: 'week',
  MONTH: 'month'
}

/**
 * 时间筛选显示文本
 */
export const TimeFilterTexts = {
  [TimeFilters.TODAY]: '今日',
  [TimeFilters.WEEK]: '本周',
  [TimeFilters.MONTH]: '本月'
}
