import api from './index'

export const notiApi = {
  list(params) {
    return api.get('/notifications', { params })
  },
  markRead(id) {
    return api.post(`/notifications/${id}/read`)
  },
  action(id, action) {
    return api.post(`/notifications/${id}/action`, { action })
  },
  remove(id) {
    return api.delete(`/notifications/${id}`)
  },
  removeAll() {
    return api.delete('/notifications')
  }
}
