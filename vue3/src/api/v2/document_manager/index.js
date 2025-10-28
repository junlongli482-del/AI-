/**
 * 文档管理API
 * 路径: /api/v2/document_manager/documents
 */
import request from '@/utils/request'

const BASE_URL = '/v2/document_manager'

/**
 * 创建文档
 * @param {Object} data - 文档信息
 * @param {string} data.title - 文档标题（必填）
 * @param {string} [data.content] - 文档内容（可选）
 * @param {string} [data.summary] - 简短摘要（可选）
 * @param {number} [data.folder_id] - 所属文件夹ID（可选）
 * @param {string} [data.file_type] - 文件类型：md或pdf，默认md
 * @returns {Promise} 文档详情
 */
export function createDocument(data) {
  return request({
    url: `${BASE_URL}/documents`,
    method: 'post',
    data
  })
}

/**
 * 获取文档列表（分页）
 * @param {Object} params - 查询参数
 * @param {number} [params.folder_id] - 文件夹ID筛选（可选）
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @returns {Promise} 文档列表
 */
export function getDocuments(params = {}) {
  return request({
    url: `${BASE_URL}/documents`,
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 20,
      folder_id: params.folder_id
    }
  })
}

/**
 * 获取文档详情
 * @param {number} docId - 文档ID
 * @returns {Promise} 文档详情
 */
export function getDocumentDetail(docId) {
  return request({
    url: `${BASE_URL}/documents/${docId}`,
    method: 'get'
  })
}

/**
 * 更新文档
 * @param {number} docId - 文档ID
 * @param {Object} data - 更新的数据
 * @param {string} [data.title] - 文档标题
 * @param {string} [data.content] - 文档内容
 * @param {string} [data.summary] - 简短摘要
 * @param {number} [data.folder_id] - 所属文件夹ID（0表示移到根目录）
 * @returns {Promise} 更新后的文档详情
 */
export function updateDocument(docId, data) {
  return request({
    url: `${BASE_URL}/documents/${docId}`,
    method: 'put',
    data
  })
}

/**
 * 删除文档
 * @param {number} docId - 文档ID
 * @returns {Promise}
 */
export function deleteDocument(docId) {
  return request({
    url: `${BASE_URL}/documents/${docId}`,
    method: 'delete'
  })
}

/**
 * 获取统计信息
 * @returns {Promise} 统计数据
 */
export function getStats() {
  return request({
    url: `${BASE_URL}/stats`,
    method: 'get'
  })
}

/**
 * 文档状态枚举
 */
export const DocumentStatus = {
  DRAFT: 'draft',           // 草稿
  PUBLISHED: 'published',   // 已发布
  REVIEW_FAILED: 'review_failed' // 审核失败
}

/**
 * 文档状态显示文本
 */
export const DocumentStatusText = {
  draft: '草稿',
  published: '已发布',
  review_failed: '审核失败'
}

/**
 * 文件类型枚举
 */
export const FileType = {
  MD: 'md',
  PDF: 'pdf'
}

/**
 * 文件类型显示文本
 */
export const FileTypeText = {
  md: 'Markdown',
  pdf: 'PDF'
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 验证文档标题
 * @param {string} title - 文档标题
 * @returns {Object} { valid: boolean, message: string }
 */
export function validateDocumentTitle(title) {
  if (!title || title.trim() === '') {
    return { valid: false, message: '文档标题不能为空' }
  }

  if (title.length > 200) {
    return { valid: false, message: '文档标题不能超过200个字符' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证文档摘要
 * @param {string} summary - 文档摘要
 * @returns {Object} { valid: boolean, message: string }
 */
export function validateDocumentSummary(summary) {
  if (!summary) {
    return { valid: true, message: '' } // 摘要可选
  }

  if (summary.length > 500) {
    return { valid: false, message: '文档摘要不能超过500个字符' }
  }

  return { valid: true, message: '' }
}
