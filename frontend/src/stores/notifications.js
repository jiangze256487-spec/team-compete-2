import { defineStore } from 'pinia'
import { notiApi } from '@/api/notifications'

// 未读通知共享状态：侧边栏红点与通知页共用，任何页面标记已读/处理后即时刷新
export const useNotiStore = defineStore('noti', {
  state: () => ({
    unread: 0
  }),
  actions: {
    async fetchUnread() {
      try {
        const list = await notiApi.list({ unread_only: true })
        this.unread = list?.length || 0
      } catch (e) {
        // 请求失败时保留上次数值，避免错误清零造成误判
      }
    }
  }
})
