import request from '@/utils/request'

// 修改密码
export function changePassword(data) {
  return request({
    url: 'v1/password_manager/change-password',
    method: 'post',
    data
  })
}

// 检查密码强度
export function checkPasswordStrength(password) {
  return request({
    url: 'v1/password_manager/check-strength',
    method: 'post',
    data: { password }
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: 'v1/password_manager/user-info',
    method: 'get'
  })
}
