import api from './index'

export const eventApi = {
  list(params) {
    return api.get('/events', { params })
  },
  categories() {
    return api.get('/events/categories')
  }
}
