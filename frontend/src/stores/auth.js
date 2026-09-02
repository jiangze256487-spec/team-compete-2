import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'

function safeParseUser(raw) {
  try {
    return JSON.parse(raw || 'null')
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('cm_token') || '',
    user: safeParseUser(localStorage.getItem('cm_user'))
  }),
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  actions: {
    _persist() {
      localStorage.setItem('cm_token', this.token)
      localStorage.setItem('cm_user', JSON.stringify(this.user))
    },
    setSession({ access_token, user }) {
      this.token = access_token
      this.user = user
      this._persist()
    },
    async login(data) {
      const res = await authApi.login(data)
      this.setSession(res)
      return res
    },
    async register(data) {
      const res = await authApi.register(data)
      this.setSession(res)
      return res
    },
    async fetchMe() {
      const user = await authApi.getMe()
      this.user = user
      this._persist()
      return user
    },
    updateUser(user) {
      this.user = user
      this._persist()
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('cm_token')
      localStorage.removeItem('cm_user')
    }
  }
})
