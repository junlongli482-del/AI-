import { defineStore } from 'pinia'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { login, getCurrentUser } from '@/api/v1/user_auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    userInfo: null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token
  },

  actions: {
    async login(loginData) {
      const response = await login(loginData)
      this.token = response.access_token
      setToken(response.access_token)
      return response
    },

    async getUserInfo() {
      const response = await getCurrentUser()
      this.userInfo = response
      return response
    },

    logout() {
      this.token = ''
      this.userInfo = null
      removeToken()
    }
  }
})
