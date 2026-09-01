<script setup>
import { ref, computed, onMounted } from 'vue'
import { notiApi } from '@/api/notifications'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const notiTab = ref('all')
const notiTabs = [
  { key: 'all', label: '全部' },
  { key: 'team', label: '组队通知' },
  { key: 'event', label: '赛事通知' },
  { key: 'system', label: '系统通知' }
]
const notifications = ref([])
const loading = ref(true)

const iconMap = {
  team: { bg: '#EEF2FF', color: '#4F46E5', path: 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z' },
  event: { bg: '#FFF7ED', color: '#F97316', path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  system: { bg: '#F0F9FF', color: '#0EA5E9', path: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' }
}

const filteredNotifications = computed(() => {
  if (notiTab.value === 'all') return notifications.value
  return notifications.value.filter((n) => n.type === notiTab.value)
})

const unreadCount = computed(() => notifications.value.filter((n) => !n.is_read).length)

function iconOf(type) {
  return iconMap[type] || iconMap.system
}

function timeStr(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}月${d.getDate()}日 ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function load() {
  loading.value = true
  try {
    notifications.value = await notiApi.list({})
  } catch (e) {
    toast.show(e)
  } finally {
    loading.value = false
  }
}

async function markRead(n) {
  if (n.is_read) return
  n.is_read = true
  try {
    await notiApi.markRead(n.id)
  } catch (e) { /* 静默 */ }
}

async function handleNotiAction(n, action) {
  try {
    await notiApi.action(n.id, action)
    n.is_read = true
    toast.show(action === 'accept' ? '已接受' : '已拒绝')
    load()
  } catch (e) {
    toast.show(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="p-8 max-w-3xl">
    <h1 class="text-2xl font-bold text-ink-primary mb-8">通知中心</h1>
    <div class="flex gap-6 mb-6">
      <span v-for="tab in notiTabs" :key="tab.key"
        class="text-sm font-medium cursor-pointer pb-2 border-b-2 transition-colors"
        :class="notiTab === tab.key ? 'text-primary border-primary' : 'text-ink-muted border-transparent hover:text-ink-secondary'"
        @click="notiTab = tab.key">{{ tab.label }}</span>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="card p-4"><div class="skeleton h-4 mb-2"></div><div class="skeleton h-3 w-2/3"></div></div>
    </div>

    <div v-else class="space-y-3">
      <div v-for="n in filteredNotifications" :key="n.id" class="card card-hover p-4 flex items-start gap-4"
        :class="{ 'bg-primary-tint/30': !n.is_read }" @click="markRead(n)">
        <div class="w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center" :style="{ background: iconOf(n.type).bg }">
          <svg class="w-5 h-5" :style="{ color: iconOf(n.type).color }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconOf(n.type).path"/></svg>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="text-sm font-medium text-ink-primary">{{ n.title }}</span>
            <span v-if="!n.is_read" class="w-2 h-2 rounded-full bg-danger flex-shrink-0"></span>
          </div>
          <p class="text-sm text-ink-secondary">{{ n.content }}</p>
          <span class="text-xs text-ink-muted mt-1 block">{{ timeStr(n.created_at) }}</span>
        </div>
        <div v-if="n.action_type" class="flex gap-2 flex-shrink-0">
          <button class="text-xs font-medium px-3 py-1.5 rounded-md gradient-brand text-white" @click.stop="handleNotiAction(n, 'accept')">接受</button>
          <button class="text-xs font-medium px-3 py-1.5 rounded-md border border-line text-ink-secondary" @click.stop="handleNotiAction(n, 'decline')">拒绝</button>
        </div>
      </div>
    </div>

    <div v-if="!loading && filteredNotifications.length === 0" class="text-center py-20">
      <div class="w-20 h-20 rounded-full bg-[#F1F5F9] mx-auto mb-4 flex items-center justify-center">
        <svg class="w-10 h-10 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
      </div>
      <p class="text-ink-muted">暂无通知</p>
    </div>
  </div>
</template>
