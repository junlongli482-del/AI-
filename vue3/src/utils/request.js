import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

// ========== API 地址配置 ==========
// 使用哪个就取消注释哪个，注释掉不用的

// 本地开发
const API_BASE_URL = 'http://localhost:8100/api'

// 公网访问
// const API_BASE_URL = 'http://ljl.api.cpolar.top/api/v1'

// ===================================

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

request.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('请求错误详情：', error.response || error)

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // 直接显示后端返回的错误信息
          if (data.detail) {
            ElMessage.error(data.detail)
            // 只有在 token 相关错误时才清除 token 并跳转
            if (data.detail.includes('过期') || data.detail.includes('无效') || data.detail.includes('Token')) {
              removeToken()
              router.push('/login')
            }
          } else {
            ElMessage.error('认证失败')
          }
          break
        case 400:
          ElMessage.error(data.detail || '请求参数错误')
          break
        case 422:
          if (data.detail && Array.isArray(data.detail)) {
            const errorMsg = data.detail.map(err => err.msg).join(', ')
            ElMessage.error(errorMsg)
          } else {
            ElMessage.error(data.detail || '数据验证失败')
          }
          break
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
        default:
          ElMessage.error(data.detail || `请求失败 (${status})`)
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查后端服务是否启动')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export default request
