import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Bearer ${auth.token}`
  return config
})

function formatDetail(detail) {
  if (Array.isArray(detail)) {
    // FastAPI 422 校验错误：detail 是数组
    return detail.map((d) => d.msg || JSON.stringify(d)).join('；')
  }
  return typeof detail === 'string' ? detail : ''
}

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const auth = useAuthStore()
    if (err.response?.status === 401 && auth.token) {
      auth.logout()
      router.push('/login')
      return Promise.reject('登录已过期，请重新登录')
    }
    const data = err.response?.data
    const detail = formatDetail(data?.detail) || data?.message || ''
    return Promise.reject(detail || '请求失败，请稍后重试')
  }
)

export default api
