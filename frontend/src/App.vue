<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const isAuthPage = computed(() => route.name === 'login')
const pageTitle = computed(() => {
  const map = { home: '首页', teams: '组队广场', 'team-detail': '队伍详情', notifications: '通知中心', profile: '个人中心' }
  return map[route.name] || '竞赛组队系统'
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div v-if="isAuthPage" class="min-h-screen">
    <router-view />
  </div>
  <div v-else class="flex h-screen overflow-hidden">
    <Sidebar :title="pageTitle" @logout="handleLogout" />
    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>
  </div>

  <transition name="slide">
    <div v-if="toast.message"
      class="fixed top-6 left-1/2 -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-lg text-white text-sm font-medium gradient-brand">
      {{ toast.message }}
    </div>
  </transition>
</template>
