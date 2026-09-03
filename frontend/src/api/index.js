import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const auth = useAuthStore()
    if (err.response?.status === 401 && auth.token) {
      auth.logout()
      window.location.href = '/login'
    }
    return Promise.reject(err.response?.data?.detail || err.response?.data?.message || '请求失败')
  }
)

export default api
