import api from './index'

export const authApi = {
  register(data) {
    return api.post('/auth/register', data)
  },
  login(data) {
    return api.post('/auth/login', data)
  },
  getMe() {
    return api.get('/users/me')
  },
  updateMe(data) {
    return api.put('/users/me', data)
  },
  updateTags(data) {
    return api.put('/users/me/tags', data)
  },
  getUser(id) {
    return api.get(`/users/${id}`)
  }
}
