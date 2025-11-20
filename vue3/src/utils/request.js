import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './auth'
import router from '@/router'

// ========== API 地址配置 ==========
// 自动根据环境使用不同的API地址
// 开发环境: http://localhost:8100/api
// 生产环境: /api (相对路径，由Nginx代理)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8100/api'

console.log('当前API地址:', API_BASE_URL)
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
      const { status, data, config } = error.response

      // 🎯 特殊处理：用户名/邮箱检查接口的404错误 - 静默处理
      if (status === 404 && config.url) {
        const isUsernameCheck = config.url.includes('/check-username/')
        const isEmailCheck = config.url.includes('/check-email/')

        if (isUsernameCheck || isEmailCheck) {
          // 静默处理，不弹提示，直接返回错误让组件处理
          return Promise.reject(error)
        }
      }

      switch (status) {
        case 401:
          if (data.detail) {
            ElMessage.error(data.detail)
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
export { API_BASE_URL }
