import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    message: '',
    timer: null
  }),
  actions: {
    show(msg, duration = 2000) {
      this.message = msg
      clearTimeout(this.timer)
      this.timer = setTimeout(() => { this.message = '' }, duration)
    }
  }
})
