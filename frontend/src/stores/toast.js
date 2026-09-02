import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    message: '',
    type: 'success', // success / error / warning / info
    timer: null
  }),
  actions: {
    show(msg, type = 'success', duration = 2000) {
      this.message = msg
      this.type = type
      clearTimeout(this.timer)
      this.timer = setTimeout(() => { this.message = '' }, duration)
    }
  }
})
