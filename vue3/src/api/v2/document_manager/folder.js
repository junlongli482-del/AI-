/**
 * 文件夹管理API
 * 路径: /api/v2/document_manager/folders
 */
import request from '@/utils/request'

const BASE_URL = '/v2/document_manager'

/**
 * 创建文件夹
 * @param {Object} data - 文件夹信息
 * @param {string} data.name - 文件夹名称
 * @param {number} [data.parent_id] - 父文件夹ID（可选）
 * @returns {Promise} 文件夹信息
 */
export function createFolder(data) {
  return request({
    url: `${BASE_URL}/folders`,
    method: 'post',
    data
  })
}

/**
 * 获取文件夹树
 * @returns {Promise} 文件夹树形结构
 */
export function getFolderTree() {
  return request({
    url: `${BASE_URL}/folders/tree`,
    method: 'get'
  })
}

/**
 * 删除文件夹
 * @param {number} folderId - 文件夹ID
 * @returns {Promise}
 */
export function deleteFolder(folderId) {
  return request({
    url: `${BASE_URL}/folders/${folderId}`,
    method: 'delete'
  })
}

/**
 * 验证文件夹名称
 * 前端验证规则：不能包含特殊字符 / \ : * ? " < > |
 * @param {string} name - 文件夹名称
 * @returns {Object} { valid: boolean, message: string }
 */
export function validateFolderName(name) {
  if (!name || name.trim() === '') {
    return { valid: false, message: '文件夹名称不能为空' }
  }

  if (name.length > 100) {
    return { valid: false, message: '文件夹名称不能超过100个字符' }
  }

  const invalidChars = /[\/\\:*?"<>|]/
  if (invalidChars.test(name)) {
    return { valid: false, message: '文件夹名称不能包含特殊字符: / \\ : * ? " < > |' }
  }

  return { valid: true, message: '' }
}
