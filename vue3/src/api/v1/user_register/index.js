import request from '@/utils/request'

// 检查用户名是否可用
export function checkUsername(username) {
  return request({
    url: `v1/user_register/check-username/${username}`,
    method: 'get'
  })
}

// 检查邮箱是否可用
export function checkEmail(email) {
  return request({
    url: `v1/user_register/check-email/${email}`,
    method: 'get'
  })
}

// 用户注册
export function register(data) {
  return request({
    url: 'v1/user_register/register',
    method: 'post',
    data
  })
}
