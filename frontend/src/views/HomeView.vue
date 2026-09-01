<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { teamApi } from '@/api/teams'
import { eventApi } from '@/api/events'
import TeamCard from '@/components/TeamCard.vue'

const router = useRouter()

const searchQuery = ref('')
const bannerIndex = ref(0)
const selectedCategory = ref('全部')
let bannerTimer = null

const banners = [
  { title: '2026 全国大学生数学建模竞赛', desc: '报名倒计时 15 天 · 已有 328 支队伍参赛' },
  { title: 'ACM-ICPC 2026 赛季启动', desc: '新赛季新挑战，寻找你的最佳搭档' },
  { title: '挑战杯 · 创新赛道开启', desc: '跨学科组队，碰撞创新火花' }
]

const eventCategories = ref(['全部'])
const events = ref([])
const teams = ref([])
const loading = ref(true)

const filteredEvents = computed(() => {
  if (selectedCategory.value === '全部') return events.value.slice(0, 4)
  return events.value.filter((e) => e.category === selectedCategory.value).slice(0, 4)
})

async function load() {
  loading.value = true
  try {
    const [cats, evts, teamRes] = await Promise.all([
      eventApi.categories(),
      eventApi.list(),
      teamApi.list({})
    ])
    eventCategories.value = ['全部', ...(cats || []).map((c) => c.name)]
    events.value = evts || []
    teams.value = teamRes?.items || teamRes || []
  } finally {
    loading.value = false
  }
}

function goSearch() {
  router.push({ name: 'teams', query: searchQuery.value ? { q: searchQuery.value } : {} })
}

onMounted(() => {
  load()
  bannerTimer = setInterval(() => {
    bannerIndex.value = (bannerIndex.value + 1) % banners.length
  }, 4000)
})
onUnmounted(() => clearInterval(bannerTimer))
</script>

<template>
  <div class="p-8 max-w-6xl">
    <!-- Search -->
    <div class="mb-8">
      <div class="relative max-w-xl">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        <input v-model="searchQuery" type="text" class="input-field pl-11 pr-4 py-3 text-base" placeholder="搜索赛事、队伍或队友标签..." @keyup.enter="goSearch">
      </div>
    </div>

    <!-- Carousel -->
    <div class="relative mb-10 rounded-xl overflow-hidden gradient-brand h-48">
      <div v-for="(banner, i) in banners" :key="i" v-show="bannerIndex === i" class="absolute inset-0 flex items-center px-10">
        <div class="text-white">
          <h2 class="text-2xl font-bold mb-2">{{ banner.title }}</h2>
          <p class="text-indigo-100 text-sm">{{ banner.desc }}</p>
        </div>
      </div>
      <div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
        <div v-for="(b, i) in banners" :key="i" class="h-2 cursor-pointer transition-all duration-200 rounded-full"
          :class="bannerIndex === i ? 'bg-primary w-6' : 'bg-[#CBD5E1] w-2'" @click="bannerIndex = i"></div>
      </div>
    </div>

    <!-- Recommended teams -->
    <section class="mb-10">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-xl font-bold text-ink-primary">推荐队伍</h2>
        <router-link :to="{ name: 'teams' }" class="text-sm text-primary font-medium cursor-pointer hover:underline">查看全部 →</router-link>
      </div>
      <div v-if="loading" class="grid grid-cols-3 gap-5">
        <div v-for="i in 3" :key="i" class="card p-5"><div class="skeleton h-4 mb-3 w-2/3"></div><div class="skeleton h-3 mb-2"></div><div class="skeleton h-3 mb-4 w-4/5"></div><div class="skeleton h-3 w-1/2"></div></div>
      </div>
      <div v-else class="grid grid-cols-3 gap-5">
        <TeamCard v-for="team in teams.slice(0, 3)" :key="team.id" :team="team" />
      </div>
    </section>

    <!-- Events -->
    <section>
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-xl font-bold text-ink-primary">当前赛事</h2>
        <div class="flex gap-2 flex-wrap">
          <span v-for="cat in eventCategories" :key="cat" class="tag cursor-pointer text-sm"
            :class="selectedCategory === cat ? 'tag-indigo' : 'tag-gray'" @click="selectedCategory = cat">{{ cat }}</span>
        </div>
      </div>
      <div v-if="loading" class="grid grid-cols-2 gap-4">
        <div v-for="i in 4" :key="i" class="card p-5"><div class="skeleton h-12 w-12 mb-3"></div><div class="skeleton h-4 mb-2"></div><div class="skeleton h-3 w-3/4"></div></div>
      </div>
      <div v-else class="grid grid-cols-2 gap-4">
        <div v-for="event in filteredEvents" :key="event.id" class="card card-hover p-5 flex gap-4">
          <div class="w-12 h-12 rounded-xl flex-shrink-0 flex items-center justify-center text-white font-bold text-lg gradient-brand">{{ (event.name || '赛')[0] }}</div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-ink-primary mb-1 truncate">{{ event.name }}</h3>
            <p class="text-xs text-ink-muted mb-2">{{ event.org || '' }}{{ event.org ? ' · ' : '' }}{{ event.deadline || '' }}</p>
            <div class="flex gap-1.5 flex-wrap">
              <span v-if="event.category" class="tag tag-purple">{{ event.category }}</span>
              <span v-if="event.teams_count != null" class="tag tag-blue">{{ event.teams_count }}支队伍参赛</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
