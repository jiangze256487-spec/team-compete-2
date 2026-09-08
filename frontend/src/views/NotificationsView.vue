<script setup>
import { ref, computed, onMounted } from 'vue'
import { notiApi } from '@/api/notifications'
import { useToastStore } from '@/stores/toast'
import { useNotiStore } from '@/stores/notifications'

const toast = useToastStore()
const notiStore = useNotiStore()

const notiTab = ref('all')
const notiTabs = [
  { key: 'all', label: '全部' },
  { key: 'team', label: '组队通知' },
  { key: 'event', label: '赛事通知' },
  { key: 'system', label: '系统通知' }
]
const notifications = ref([])
const loading = ref(true)
const processingId = ref(0)

const iconMap = {
  team: { bg: '#EEF2FF', color: '#4F46E5', path: 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z' },
  event: { bg: '#FFF7ED', color: '#F97316', path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  system: { bg: '#F0F9FF', color: '#0EA5E9', path: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' }
}

// 只有待处理的「入队申请 / 入队邀请」才需要接受/拒绝操作；
// 入队成功、离队、系统消息等告知类通知一律不展示操作按钮（action_type 为 "team"/"" 等时隐藏）。
const ACTIONABLE_ACTION_TYPES = ['request', 'invite']

function isActionable(n) {
  return ACTIONABLE_ACTION_TYPES.includes(n.action_type)
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
    toast.show(e, 'error')
  } finally {
    loading.value = false
  }
}

async function markRead(n) {
  if (n.is_read) return
  n.is_read = true
  try {
    await notiApi.markRead(n.id)
    notiStore.fetchUnread()
  } catch (e) {
    // 标记失败时回滚本地状态，避免界面与后端不一致（红点不消失）
    n.is_read = false
    toast.show(e, 'error')
  }
}

async function handleNotiAction(n, action) {
  if (processingId.value) return
  processingId.value = n.id
  try {
    await notiApi.action(n.id, action)
    n.is_read = true
    n.action_type = '' // 已处理，立即隐藏操作按钮
    toast.show(action === 'accept' ? '已接受' : '已拒绝')
    notiStore.fetchUnread()
    load()
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    processingId.value = 0
  }
}

const removingId = ref(0)

async function removeNoti(n) {
  if (removingId.value) return
  removingId.value = n.id
  try {
    await notiApi.remove(n.id)
    notifications.value = notifications.value.filter((x) => x.id !== n.id)
    notiStore.fetchUnread()
    toast.show('已删除')
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    removingId.value = 0
  }
}

async function clearAll() {
  if (!window.confirm('确定清空全部通知？此操作不可撤销。')) return
  try {
    await notiApi.removeAll()
    notifications.value = []
    notiStore.fetchUnread()
    toast.show('已清空全部通知')
  } catch (e) {
    toast.show(e, 'error')
  }
}

onMounted(load)
</script>

<template>
  <!-- 容器宽度与组队广场（TeamsView）保持一致：空状态图标因此与「暂无队伍」位置对齐 -->
  <div class="p-4 md:p-8 max-w-6xl">
    <!-- 正文（标题/Tab/列表）维持窄栏阅读宽度 -->
    <div class="max-w-3xl">
      <div class="flex items-center justify-between mb-8">
        <h1 class="text-2xl font-bold text-ink-primary">通知中心</h1>
        <button v-if="notifications.length" class="text-sm text-ink-muted hover:text-danger transition-colors"
          @click="clearAll">清空全部</button>
      </div>
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
        <div v-for="n in filteredNotifications" :key="n.id" class="card card-hover p-4 flex items-start gap-4 group"
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
          <div v-if="isActionable(n)" class="flex gap-2 flex-shrink-0">
            <button class="text-xs font-medium px-3 py-1.5 rounded-md gradient-brand text-white disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="processingId === n.id" @click.stop="handleNotiAction(n, 'accept')">
              {{ processingId === n.id ? '处理中...' : '接受' }}
            </button>
            <button class="text-xs font-medium px-3 py-1.5 rounded-md border border-line text-ink-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="processingId === n.id" @click.stop="handleNotiAction(n, 'decline')">
              {{ processingId === n.id ? '处理中...' : '拒绝' }}
            </button>
          </div>
          <button class="flex-shrink-0 text-ink-muted hover:text-danger opacity-0 group-hover:opacity-100 transition-opacity p-1"
            :disabled="removingId === n.id" @click.stop="removeNoti(n)" title="删除">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态：置于外层容器、与列表窄栏同级，居中基准与组队广场空状态一致 -->
    <div v-if="!loading && filteredNotifications.length === 0" class="text-center py-20">
      <div class="w-20 h-20 rounded-full bg-[#F1F5F9] mx-auto mb-4 flex items-center justify-center">
        <svg class="w-10 h-10 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
      </div>
      <p class="text-ink-muted">暂无通知</p>
      <p class="text-xs text-ink-muted mt-1">组队动态会实时通知你</p>
    </div>
  </div>
</template>
