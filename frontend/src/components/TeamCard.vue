<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  team: { type: Object, required: true }
})

const router = useRouter()

const avatarBg = [
  'linear-gradient(135deg, #4F46E5, #7C3AED)',
  'linear-gradient(135deg, #0EA5E9, #6366F1)',
  'linear-gradient(135deg, #7C3AED, #EC4899)',
  'linear-gradient(135deg, #F97316, #EF4444)'
]

function bgFor(id) {
  return avatarBg[id % avatarBg.length]
}

function goDetail() {
  router.push(`/teams/${props.team.id}`)
}
</script>

<template>
  <div class="card card-hover p-5 cursor-pointer" @click="goDetail">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-3">
        <div class="avatar" :style="{ background: bgFor(team.id) }">{{ (team.name || '队')[0] }}</div>
        <div class="min-w-0">
          <h3 class="font-semibold text-ink-primary truncate">{{ team.name }}</h3>
          <span class="text-xs text-ink-muted">{{ team.school || '未知学校' }}</span>
        </div>
      </div>
      <span class="tag flex-shrink-0" :class="team.status === '招募中' ? 'tag-green' : 'tag-orange'">{{ team.status }}</span>
    </div>
    <p class="text-sm text-ink-secondary mb-3 line-clamp-2">{{ team.desc || '暂无描述' }}</p>
    <div class="flex flex-wrap gap-1.5 mb-3">
      <span v-if="team.event_name" class="tag tag-indigo">{{ team.event_name }}</span>
      <span v-for="t in (team.tags || [])" :key="t" class="tag tag-gray">{{ t }}</span>
    </div>
    <div class="flex items-center justify-between text-xs text-ink-muted pt-3 border-t border-[#F1F5F9]">
      <span>{{ team.members_count }}/{{ team.max_members }} 人 · 队长 {{ team.leader_name || '—' }}</span>
    </div>
  </div>
</template>
