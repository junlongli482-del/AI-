import request from '@/utils/request'

// ==================== 会话管理 ====================

/**
 * 创建编辑器会话
 * @param {Object} data - 会话数据
 * @param {number} [data.document_id] - 文档ID（编辑现有文档时传入）
 * @param {string} [data.title] - 文档标题
 * @param {string} [data.content] - 初始内容
 * @param {string} data.session_type - 会话类型：new_document | edit_document
 */
export const createSession = (data) => {
  return request({
    url: '/v2/md_editor/sessions',
    method: 'post',
    data
  })
}

/**
 * 获取会话列表
 * @param {Object} params - 查询参数
 * @param {number} [params.skip=0] - 跳过记录数
 * @param {number} [params.limit=20] - 返回记录数
 */
export const getSessions = (params = {}) => {
  return request({
    url: '/v2/md_editor/sessions',
    method: 'get',
    params: {
      skip: 0,
      limit: 20,
      ...params
    }
  })
}

/**
 * 获取会话详情
 * @param {number} sessionId - 会话ID
 */
export const getSessionDetail = (sessionId) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}`,
    method: 'get'
  })
}

/**
 * 更新会话内容
 * @param {number} sessionId - 会话ID
 * @param {Object} data - 更新数据
 * @param {string} [data.title] - 标题
 * @param {string} [data.content] - 内容
 * @param {boolean} [data.is_draft] - 是否为草稿
 */
export const updateSession = (sessionId, data) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}`,
    method: 'put',
    data
  })
}

/**
 * 删除编辑会话
 * @param {number} sessionId - 会话ID
 */
export const deleteSession = (sessionId) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}`,
    method: 'delete'
  })
}

/**
 * 保存为正式文档
 * @param {number} sessionId - 会话ID
 * @param {Object} data - 保存数据
 * @param {string} data.title - 文档标题
 * @param {number} [data.folder_id] - 文件夹ID
 * @param {string} [data.summary] - 文档摘要
 */
export const saveAsDocument = (sessionId, data) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}/save-document`,
    method: 'post',
    data
  })
}

// ==================== AI优化功能 ====================

/**
 * AI内容优化
 * @param {number} sessionId - 会话ID
 * @param {Object} data - 优化数据
 * @param {string} data.content - 要优化的内容
 * @param {string} data.optimization_type - 优化类型：general | grammar | structure | expand
 */
export const optimizeContent = (sessionId, data) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}/optimize`,
    method: 'post',
    data,
    timeout: 60000  // 只对AI优化接口设置60秒超时
  })
}
/**
 * 应用优化结果
 * @param {number} sessionId - 会话ID
 * @param {number} optimizationId - 优化ID
 */
export const applyOptimization = (sessionId, optimizationId) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}/apply-optimization/${optimizationId}`,
    method: 'post'
  })
}

/**
 * 获取优化历史记录
 * @param {number} sessionId - 会话ID
 */
export const getOptimizationHistory = (sessionId) => {
  return request({
    url: `/v2/md_editor/sessions/${sessionId}/optimizations`,
    method: 'get'
  })
}

// ==================== 配置统计 ====================

/**
 * 获取编辑器配置
 */
export const getEditorConfig = () => {
  return request({
    url: '/v2/md_editor/config',
    method: 'get'
  })
}

/**
 * 获取编辑器统计
 */
export const getEditorStats = () => {
  return request({
    url: '/v2/md_editor/stats',
    method: 'get'
  })
}

// ==================== 工具函数 ====================

/**
 * 优化类型映射
 */
export const OptimizationTypes = {
  general: '通用优化',
  grammar: '语法检查',
  structure: '结构优化',
  expand: '内容扩展'
}

/**
 * 会话类型映射
 */
export const SessionTypes = {
  new_document: '新建文档',
  edit_document: '编辑文档'
}

/**
 * 验证会话标题
 * @param {string} title - 标题
 * @returns {boolean} 是否有效
 */
export const validateSessionTitle = (title) => {
  if (!title || typeof title !== 'string') {
    return false
  }
  const trimmed = title.trim()
  return trimmed.length > 0 && trimmed.length <= 200
}

/**
 * 验证内容长度
 * @param {string} content - 内容
 * @returns {boolean} 是否有效
 */
export const validateContentLength = (content) => {
  if (!content || typeof content !== 'string') {
    return true // 空内容允许
  }
  return content.length <= 50000 // 最大50k字符
}

/**
 * 格式化字数统计
 * @param {string} content - 内容
 * @returns {Object} 统计信息
 */
export const getContentStats = (content) => {
  if (!content || typeof content !== 'string') {
    return {
      characters: 0,
      charactersNoSpaces: 0,
      words: 0,
      lines: 0
    }
  }

  const characters = content.length
  const charactersNoSpaces = content.replace(/\s/g, '').length
  const words = content.trim() ? content.trim().split(/\s+/).length : 0
  const lines = content.split('\n').length

  return {
    characters,
    charactersNoSpaces,
    words,
    lines
  }
}

/**
 * 生成默认标题
 * @param {string} content - 内容
 * @returns {string} 默认标题
 */
export const generateDefaultTitle = (content) => {
  if (!content || typeof content !== 'string') {
    return '未命名文档'
  }

  // 尝试从第一行提取标题
  const firstLine = content.split('\n')[0].trim()

  // 如果是Markdown标题格式
  const titleMatch = firstLine.match(/^#+\s*(.+)$/)
  if (titleMatch) {
    return titleMatch[1].substring(0, 50) // 最多50字符
  }

  // 如果第一行有内容
  if (firstLine) {
    return firstLine.substring(0, 50)
  }

  return '未命名文档'
}

/**
 * 防抖函数（用于自动保存）
 * @param {Function} func - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export const debounce = (func, delay) => {
  let timeoutId
  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}
