import request from '@/utils/request'

// 获取用户资料
export function getUserProfile() {
  return request({
    url: '/user_profile/me',
    method: 'get'
  })
}

// 更新昵称
export function updateNickname(nickname) {
  return request({
    url: '/user_profile/nickname',
    method: 'put',
    data: { nickname }
  })
}

// 检查昵称可用性
export function checkNickname(nickname) {
  return request({
    url: `/user_profile/check-nickname/${nickname}`,
    method: 'get'
  })
}

// 退出登录
export function logout() {
  return request({
    url: '/user_profile/logout',
    method: 'post'
  })
}
