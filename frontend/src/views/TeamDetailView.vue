<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { teamApi } from '@/api/teams'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const toast = useToastStore()
const auth = useAuthStore()

const team = ref(null)
const loading = ref(true)
const applying = ref(false)

const isLeader = computed(() => team.value && team.value.leader_id === auth.user?.id)
const isMember = computed(() => team.value && (team.value.members || []).some((m) => m.user_id === auth.user?.id))
const vacancies = computed(() => (team.value ? team.value.max_members - team.value.members_count : 0))

async function load() {
  loading.value = true
  try {
    team.value = await teamApi.detail(route.params.id)
  } catch (e) {
    toast.show(e)
  } finally {
    loading.value = false
  }
}

async function applyToTeam() {
  applying.value = true
  try {
    const res = await teamApi.apply(team.value.id)
    toast.show(res.message || '已发送入队申请')
  } catch (e) {
    toast.show(e)
  } finally {
    applying.value = false
  }
}

async function leaveTeam() {
  try {
    const res = await teamApi.leave(team.value.id)
    toast.show(res.message || '已退出队伍')
    router.push('/teams')
  } catch (e) {
    toast.show(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="p-8 max-w-4xl">
    <button class="flex items-center gap-1 text-sm text-ink-secondary hover:text-primary mb-6" @click="router.push('/teams')">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      返回组队广场
    </button>

    <div v-if="loading" class="card p-8 space-y-4">
      <div class="skeleton h-10 w-2/3"></div>
      <div class="skeleton h-4 w-1/3"></div>
      <div class="skeleton h-24"></div>
    </div>

    <div v-else-if="team" class="card p-8">
      <div class="flex items-start justify-between mb-6">
        <div class="flex items-center gap-4">
          <div class="avatar avatar-lg">{{ (team.name || '队')[0] }}</div>
          <div>
            <h1 class="text-2xl font-bold text-ink-primary">{{ team.name }}</h1>
            <p class="text-sm text-ink-secondary mt-1">{{ team.school }} · 队长 {{ team.leader_name }}</p>
          </div>
        </div>
        <span class="tag text-sm px-4 py-1.5" :class="team.status === '招募中' ? 'tag-green' : 'tag-orange'">{{ team.status }}</span>
      </div>

      <div class="grid grid-cols-3 gap-4 mb-6 p-4 bg-page rounded-xl">
        <div class="text-center"><div class="text-2xl font-bold text-primary">{{ team.members_count }}</div><div class="text-xs text-ink-muted">当前人数</div></div>
        <div class="text-center border-x border-line"><div class="text-2xl font-bold text-ink-primary">{{ team.max_members }}</div><div class="text-xs text-ink-muted">队伍上限</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-cta">{{ vacancies }}</div><div class="text-xs text-ink-muted">空缺名额</div></div>
      </div>

      <div class="mb-6">
        <h3 class="font-semibold text-ink-primary mb-2">队伍描述</h3>
        <p class="text-sm text-ink-secondary leading-relaxed">{{ team.desc || '暂无详细描述。这支队伍正在寻找志同道合的队友一起参加竞赛。' }}</p>
      </div>

      <div class="mb-6">
        <h3 class="font-semibold text-ink-primary mb-2">赛事与标签</h3>
        <div class="flex flex-wrap gap-2">
          <span v-if="team.event_name" class="tag tag-indigo text-sm">{{ team.event_name }}</span>
          <span v-for="t in (team.tags || [])" :key="t" class="tag tag-purple text-sm">{{ t }}</span>
        </div>
      </div>

      <div class="mb-8">
        <h3 class="font-semibold text-ink-primary mb-3">当前成员</h3>
        <div class="space-y-3">
          <div v-for="m in (team.members || [])" :key="m.user_id" class="flex items-center justify-between p-3 bg-page rounded-lg">
            <div class="flex items-center gap-3">
              <div class="avatar">{{ (m.name || '?')[0] }}</div>
              <div>
                <span class="text-sm font-medium text-ink-primary">{{ m.name }}</span>
                <span v-if="m.is_leader" class="tag tag-orange ml-2">队长</span>
                <div class="text-xs text-ink-muted mt-0.5">{{ m.school }} · {{ m.grade }}</div>
              </div>
            </div>
            <div class="flex gap-1.5 flex-wrap justify-end">
              <span v-for="t in (m.skills || [])" :key="t" class="tag tag-indigo">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-3">
        <button v-if="!isMember" class="btn-cta flex-1 py-3" :disabled="applying" @click="applyToTeam">申请加入</button>
        <button v-else class="btn-outline flex-1 py-3" @click="leaveTeam">退出队伍</button>
      </div>
    </div>
  </div>
</template>
