import request from '@/utils/request'

// 修改密码
export function changePassword(data) {
  return request({
    url: '/password_manager/change-password',
    method: 'post',
    data
  })
}

// 检查密码强度
export function checkPasswordStrength(password) {
  return request({
    url: '/password_manager/check-strength',
    method: 'post',
    data: { password }
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/password_manager/user-info',
    method: 'get'
  })
}
