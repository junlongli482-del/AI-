/**
 * 文件上传API
 * 路径: /api/v2/file_upload
 */
import request from '@/utils/request'

const BASE_URL = '/v2/file_upload'

/**
 * 获取上传配置
 * @returns {Promise} 上传配置信息
 */
export function getUploadConfig() {
  return request({
    url: `${BASE_URL}/config`,
    method: 'get'
  })
}

/**
 * 验证文件（不保存）
 * @param {File} file - 要验证的文件
 * @returns {Promise} 验证结果
 */
export function validateFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: `${BASE_URL}/validate`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 上传文件
 * @param {File} file - 要上传的文件
 * @param {Function} onProgress - 上传进度回调
 * @returns {Promise} 上传结果
 */
export function uploadFile(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: `${BASE_URL}/upload`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    }
  })
}

/**
 * 获取上传历史
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @param {string} [params.status_filter] - 状态筛选
 * @returns {Promise} 上传历史列表
 */
export function getUploadHistory(params = {}) {
  return request({
    url: `${BASE_URL}/uploads`,
    method: 'get',
    params: {
      page: params.page || 1,
      page_size: params.page_size || 20,
      status_filter: params.status_filter
    }
  })
}

/**
 * 获取上传详情
 * @param {number} uploadId - 上传记录ID
 * @returns {Promise} 上传详情
 */
export function getUploadDetail(uploadId) {
  return request({
    url: `${BASE_URL}/uploads/${uploadId}`,
    method: 'get'
  })
}

/**
 * 从上传文件创建文档
 * @param {Object} data - 文档信息
 * @param {number} data.upload_id - 上传记录ID
 * @param {string} data.title - 文档标题
 * @param {string} [data.summary] - 文档摘要（可选）
 * @param {number} [data.folder_id] - 文件夹ID（可选）
 * @returns {Promise} 创建结果
 */
export function createDocumentFromUpload(data) {
  return request({
    url: `${BASE_URL}/create-document`,
    method: 'post',
    data
  })
}

/**
 * 删除上传记录
 * @param {number} uploadId - 上传记录ID
 * @returns {Promise}
 */
export function deleteUploadRecord(uploadId) {
  return request({
    url: `${BASE_URL}/uploads/${uploadId}`,
    method: 'delete'
  })
}

/**
 * 获取上传统计
 * @returns {Promise} 统计信息
 */
export function getUploadStats() {
  return request({
    url: `${BASE_URL}/stats`,
    method: 'get'
  })
}

/**
 * 上传状态枚举
 */
export const UploadStatus = {
  UPLOADING: 'uploading',       // 上传中
  UPLOADED: 'uploaded',         // 已上传
  VALIDATED: 'validated',       // 已验证
  FAILED: 'failed',             // 失败
  DELETED: 'deleted'            // 已删除
}

/**
 * 上传状态显示文本
 */
export const UploadStatusText = {
  uploading: '上传中',
  uploaded: '已上传',
  validated: '已验证',
  failed: '失败',
  deleted: '已删除'
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
 * 从文件名提取标题（去掉扩展名）
 * @param {string} filename - 文件名
 * @returns {string} 标题
 */
export function extractTitleFromFilename(filename) {
  if (!filename) return ''
  return filename.replace(/\.(md|pdf)$/i, '')
}

/**
 * 验证文件类型
 * @param {File} file - 文件对象
 * @returns {Object} { valid: boolean, message: string }
 */
export function validateFileType(file) {
  const allowedExtensions = ['.md', '.pdf']
  const fileName = file.name.toLowerCase()
  const isValid = allowedExtensions.some(ext => fileName.endsWith(ext))

  if (!isValid) {
    return {
      valid: false,
      message: '仅支持 MD 和 PDF 格式文件'
    }
  }

  return { valid: true, message: '' }
}

/**
 * 验证文件大小
 * @param {File} file - 文件对象
 * @returns {Object} { valid: boolean, message: string }
 */
export function validateFileSize(file) {
  const fileName = file.name.toLowerCase()
  const fileSizeMB = file.size / (1024 * 1024)

  if (fileName.endsWith('.md') && fileSizeMB > 20) {
    return {
      valid: false,
      message: 'MD文件不能超过20MB'
    }
  }

  if (fileName.endsWith('.pdf') && fileSizeMB > 100) {
    return {
      valid: false,
      message: 'PDF文件不能超过100MB'
    }
  }

  return { valid: true, message: '' }
}
