<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { teamApi } from '@/api/teams'
import { eventApi } from '@/api/events'
import { useToastStore } from '@/stores/toast'
import { allSkillTags, grades } from '@/constants/tags'
import TeamCard from '@/components/TeamCard.vue'
import Modal from '@/components/Modal.vue'

const route = useRoute()
const toast = useToastStore()

const teams = ref([])
const loading = ref(true)

const teamSearch = ref(route.query.q || '')
const teamFilter = ref({ event: route.query.event || '', skill: '', grade: '' })
const events = ref([])
const categories = ref([])
let searchTimer = null

// 赛事下拉：优先真实赛事；数据库暂无赛事时回退到赛事分类，保证可创建队伍
const eventOptions = computed(() =>
  events.value.length ? events.value.map((e) => e.name) : categories.value
)

async function fetchTeams() {
  loading.value = true
  try {
    const params = {
      search: teamSearch.value || undefined,
      event: teamFilter.value.event || undefined,
      skill: teamFilter.value.skill || undefined,
      grade: teamFilter.value.grade || undefined
    }
    const list = await teamApi.list(params)
    teams.value = list || []
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    loading.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const [evts, cats] = await Promise.all([eventApi.list(), eventApi.categories()])
    events.value = evts || []
    categories.value = (cats || []).map((c) => c.name)
    await fetchTeams()
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    loading.value = false
  }
}

// 筛选条件变化 → 防抖后请求后端
watch([teamSearch, () => teamFilter.value.event, () => teamFilter.value.skill, () => teamFilter.value.grade], () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchTeams, 300)
})

// 从首页搜索 / 赛事卡片跳转进入时同步筛选条件
watch(() => route.query, (q) => {
  teamSearch.value = q.q || ''
  teamFilter.value.event = q.event || ''
}, { deep: true })

// Create team
const showCreateTeam = ref(false)
const creating = ref(false)
const newTeam = ref({ name: '', event_name: '', tags: [], max_members: 4, desc: '' })

function toggleTeamTag(tag) {
  const idx = newTeam.value.tags.indexOf(tag)
  if (idx >= 0) newTeam.value.tags.splice(idx, 1)
  else newTeam.value.tags.push(tag)
}

function openCreateTeam() {
  newTeam.value = { name: '', event_name: '', tags: [], max_members: 4, desc: '' }
  showCreateTeam.value = true
}

async function handleCreateTeam() {
  if (!newTeam.value.name || !newTeam.value.event_name) {
    toast.show('请填写队伍名称和赛事', 'warning')
    return
  }
  creating.value = true
  try {
    await teamApi.create(newTeam.value)
    toast.show('队伍创建成功')
    showCreateTeam.value = false
    fetchTeams()
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="p-4 md:p-8 max-w-6xl">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-2xl font-bold text-ink-primary">组队广场</h1>
      <button class="btn-cta flex items-center gap-2" @click="openCreateTeam">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        创建队伍
      </button>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-6 flex flex-wrap items-center gap-4">
      <div class="relative flex-1 min-w-[200px]">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        <input v-model="teamSearch" type="text" class="input-field pl-9 py-2 text-sm" placeholder="搜索队伍、赛事或标签...">
      </div>
      <select v-model="teamFilter.event" class="input-field w-auto py-2 text-sm">
        <option value="">全部赛事</option>
        <option v-for="e in eventOptions" :key="e" :value="e">{{ e }}</option>
      </select>
      <select v-model="teamFilter.skill" class="input-field w-auto py-2 text-sm">
        <option value="">技能标签</option>
        <option v-for="s in allSkillTags" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="teamFilter.grade" class="input-field w-auto py-2 text-sm">
        <option value="">年级</option>
        <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
      </select>
    </div>

    <!-- Team Cards -->
    <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <div v-for="i in 4" :key="i" class="card p-6"><div class="skeleton h-12 w-12 mb-3"></div><div class="skeleton h-4 mb-2"></div><div class="skeleton h-3 mb-4"></div><div class="skeleton h-3 w-1/2"></div></div>
    </div>
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <TeamCard v-for="team in teams" :key="team.id" :team="team" />
    </div>

    <!-- Empty State -->
    <div v-if="!loading && teams.length === 0" class="text-center py-20">
      <div class="w-20 h-20 rounded-full bg-primary-tint mx-auto mb-4 flex items-center justify-center">
        <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      </div>
      <p class="text-ink-secondary">没有找到匹配的队伍，试试调整筛选条件</p>
    </div>

    <!-- Create Team Modal -->
    <Modal v-model="showCreateTeam" title="创建队伍">
      <div class="space-y-4">
        <div>
          <label for="new-team-name" class="text-sm font-medium text-ink-primary block mb-1.5">队伍名称</label>
          <input id="new-team-name" v-model="newTeam.name" type="text" maxlength="128" class="input-field" placeholder="给你的队伍起个名字">
        </div>
        <div>
          <label for="new-team-event" class="text-sm font-medium text-ink-primary block mb-1.5">参赛赛事</label>
          <select id="new-team-event" v-model="newTeam.event_name" class="input-field">
            <option value="">选择赛事</option>
            <option v-for="e in eventOptions" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">队伍标签</label>
          <div class="flex flex-wrap gap-2 mb-2">
            <span v-for="t in allSkillTags" :key="t" class="tag cursor-pointer text-sm"
              :class="newTeam.tags.includes(t) ? 'tag-indigo' : 'tag-gray'" @click="toggleTeamTag(t)">{{ t }}</span>
          </div>
        </div>
        <div>
          <label for="new-team-max" class="text-sm font-medium text-ink-primary block mb-1.5">队伍人数上限</label>
          <input id="new-team-max" v-model.number="newTeam.max_members" type="number" min="2" max="10" class="input-field">
        </div>
        <div>
          <label for="new-team-desc" class="text-sm font-medium text-ink-primary block mb-1.5">队伍描述</label>
          <textarea id="new-team-desc" v-model="newTeam.desc" class="input-field" rows="3" maxlength="2000" placeholder="描述你的队伍目标、期望的队友..."></textarea>
        </div>
      </div>
      <div class="flex gap-3 mt-8">
        <button class="btn-outline flex-1" @click="showCreateTeam = false">取消</button>
        <button class="btn-primary flex-1 py-3" :disabled="creating" @click="handleCreateTeam">{{ creating ? '创建中...' : '创建队伍' }}</button>
      </div>
    </Modal>
  </div>
</template>
