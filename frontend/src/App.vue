<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { titleFor } from '@/constants/titles'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const isAuthPage = computed(() => route.name === 'login')
const pageTitle = computed(() => titleFor(route.name))

const mobileNav = [
  { name: 'home', label: '首页' },
  { name: 'teams', label: '组队广场' },
  { name: 'notifications', label: '通知' },
  { name: 'profile', label: '个人中心' }
]

const toastClass = computed(() => ({
  success: 'gradient-brand',
  error: 'bg-danger',
  warning: 'bg-warning',
  info: 'bg-info'
}[toast.type] || 'gradient-brand'))

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
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 移动端顶栏 -->
      <header class="lg:hidden bg-white border-b border-line px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg gradient-brand flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          </div>
          <span class="font-bold text-ink-primary">CompeteMate</span>
        </div>
        <span class="text-sm text-ink-secondary">{{ pageTitle }}</span>
        <button class="text-sm text-ink-secondary" @click="handleLogout">退出</button>
      </header>
      <!-- 移动端导航 -->
      <nav class="lg:hidden bg-white border-b border-line flex overflow-x-auto">
        <router-link v-for="item in mobileNav" :key="item.name" :to="{ name: item.name }"
          class="flex-1 text-center text-sm py-2.5 whitespace-nowrap"
          :class="route.name === item.name ? 'text-primary font-medium border-b-2 border-primary' : 'text-ink-muted'">
          {{ item.label }}
        </router-link>
      </nav>
      <main class="flex-1 overflow-y-auto">
        <router-view />
      </main>
    </div>
  </div>

  <transition name="slide">
    <div v-if="toast.message"
      class="fixed top-6 left-1/2 -translate-x-1/2 z-[200] px-6 py-3 rounded-xl shadow-lg text-white text-sm font-medium"
      :class="toastClass">
      {{ toast.message }}
    </div>
  </transition>
</template>
