import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { titleFor } from '@/constants/titles'

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/teams', name: 'teams', component: () => import('@/views/TeamsView.vue') },
  { path: '/teams/:id', name: 'team-detail', component: () => import('@/views/TeamDetailView.vue') },
  { path: '/notifications', name: 'notifications', component: () => import('@/views/NotificationsView.vue') },
  { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.token) return { name: 'login' }
  if (to.name === 'login' && auth.token) return { name: 'home' }
})

router.afterEach((to) => {
  document.title = `${titleFor(to.name)} - CompeteMate`
})

export default router
