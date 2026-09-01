import api from './index'

export const teamApi = {
  list(params) {
    return api.get('/teams', { params })
  },
  create(data) {
    return api.post('/teams', data)
  },
  detail(id) {
    return api.get(`/teams/${id}`)
  },
  update(id, data) {
    return api.patch(`/teams/${id}`, data)
  },
  remove(id) {
    return api.delete(`/teams/${id}`)
  },
  apply(id) {
    return api.post(`/teams/${id}/apply`)
  },
  invite(id, userId) {
    return api.post(`/teams/${id}/invite`, null, { params: { invitee_id: userId } })
  },
  leave(id) {
    return api.post(`/teams/${id}/leave`)
  }
}
