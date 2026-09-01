<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { notiApi } from '@/api/notifications'

defineProps({ title: String })
defineEmits(['logout'])

const route = useRoute()
const auth = useAuthStore()

const unreadCount = ref(0)
let pollTimer = null

async function fetchUnread() {
  try {
    const list = await notiApi.list({ unread_only: true })
    unreadCount.value = list?.length || 0
  } catch (e) {
    unreadCount.value = 0
  }
}

onMounted(() => {
  fetchUnread()
  pollTimer = setInterval(fetchUnread, 15000)
})
onUnmounted(() => clearInterval(pollTimer))

const navItems = [
  { name: 'home', label: '首页', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'teams', label: '组队广场', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' },
  { name: 'notifications', label: '通知', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { name: 'profile', label: '个人中心', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' }
]

function isActive(name) {
  if (name === 'teams') return ['teams', 'team-detail'].includes(route.name)
  return route.name === name
}
</script>

<template>
  <aside class="w-60 bg-white border-r border-line flex flex-col flex-shrink-0">
    <div class="p-5 border-b border-line">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl gradient-brand flex items-center justify-center">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        </div>
        <span class="font-bold text-ink-primary text-lg">CompeteMate</span>
      </div>
    </div>
    <nav class="flex-1 p-3 space-y-1">
      <router-link v-for="item in navItems" :key="item.name" :to="{ name: item.name }"
        class="nav-item" :class="{ active: isActive(item.name) }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/></svg>
        {{ item.label }}
        <span v-if="item.name === 'notifications' && unreadCount > 0" class="badge">{{ unreadCount }}</span>
      </router-link>
    </nav>
    <div class="p-3 border-t border-line">
      <div class="nav-item" @click="$emit('logout')">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
        退出登录
      </div>
    </div>
  </aside>
</template>
