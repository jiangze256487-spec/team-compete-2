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
    toast.show(e, 'error')
  } finally {
    leaving.value = false
  }
}

// ===== 队长管理 =====
const showManage = ref(false)
const showInvite = ref(false)
const saving = ref(false)
const removingId = ref(0)
const inviteId = ref('')
const editForm = ref({ name: '', event_name: '', max_members: 4, desc: '', tags: [] })

function toggleEditTag(tag) {
  const idx = editForm.value.tags.indexOf(tag)
  if (idx >= 0) editForm.value.tags.splice(idx, 1)
  else editForm.value.tags.push(tag)
}

async function openManage() {
  try {
    if (!events.value.length && !categories.value.length) {
      const [evts, cats] = await Promise.all([eventApi.list(), eventApi.categories()])
      events.value = evts || []
      categories.value = (cats || []).map((c) => c.name)
    }
    editForm.value = {
      name: team.value.name,
      event_name: team.value.event_name,
      max_members: team.value.max_members,
      desc: team.value.desc,
      tags: [...(team.value.tags || [])]
    }
    showManage.value = true
  } catch (e) {
    toast.show(e, 'error')
  }
}

async function saveTeam() {
  if (!editForm.value.name) {
    toast.show('队伍名称不能为空', 'warning')
    return
  }
  saving.value = true
  try {
    team.value = await teamApi.update(team.value.id, editForm.value)
    toast.show('队伍信息已更新')
    showManage.value = false
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    saving.value = false
  }
}

async function disbandTeam() {
  if (!window.confirm('确定解散队伍？此操作不可撤销。')) return
  try {
    await teamApi.remove(team.value.id)
    toast.show('队伍已解散')
    router.push('/teams')
  } catch (e) {
    toast.show(e, 'error')
  }
}

async function sendInvite() {
  const id = Number(inviteId.value)
  if (!id || !Number.isInteger(id)) {
    toast.show('请输入有效的用户 ID', 'warning')
    return
  }
  try {
    const res = await teamApi.invite(team.value.id, id)
    toast.show(res.message || '邀请已发送')
    inviteId.value = ''
    showInvite.value = false
  } catch (e) {
    toast.show(e, 'error')
    toast.show(e)
  }
}

async function removeMember(member) {
  if (!window.confirm(`确定将 ${member.name} 移出队伍？`)) return
  removingId.value = member.user_id
  try {
    const res = await teamApi.removeMember(team.value.id, member.user_id)
    toast.show(res.message || '已移除成员')
    await load()
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    removingId.value = 0
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

    <!-- 管理队伍 Modal -->
    <Modal v-model="showManage" title="管理队伍">
      <div class="space-y-4">
        <div>
          <label for="edit-team-name" class="text-sm font-medium text-ink-primary block mb-1.5">队伍名称</label>
          <input id="edit-team-name" v-model="editForm.name" type="text" maxlength="128" class="input-field">
        </div>
        <div>
          <label for="edit-team-event" class="text-sm font-medium text-ink-primary block mb-1.5">参赛赛事</label>
          <select id="edit-team-event" v-model="editForm.event_name" class="input-field">
            <option value="">选择赛事</option>
            <option v-for="e in eventOptions" :key="e" :value="e">{{ e }}</option>
          </select>
        </div>
        <div>
          <label for="edit-team-max" class="text-sm font-medium text-ink-primary block mb-1.5">队伍人数上限</label>
          <input id="edit-team-max" v-model.number="editForm.max_members" type="number" min="2" max="10" class="input-field">
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">队伍标签</label>
          <div class="flex flex-wrap gap-2">
            <span v-for="t in allSkillTags" :key="t" class="tag cursor-pointer text-sm"
              :class="editForm.tags.includes(t) ? 'tag-indigo' : 'tag-gray'" @click="toggleEditTag(t)">{{ t }}</span>
          </div>
        </div>
        <div>
          <label for="edit-team-desc" class="text-sm font-medium text-ink-primary block mb-1.5">队伍描述</label>
          <textarea id="edit-team-desc" v-model="editForm.desc" class="input-field" rows="3" maxlength="2000"></textarea>
        </div>
        <!-- 成员管理（移除队友） -->
        <div v-if="(team.members || []).some((m) => !m.is_leader)">
          <h3 class="text-sm font-medium text-ink-primary mb-3">成员管理</h3>
          <div class="space-y-2">
            <div v-for="m in (team.members || []).filter((x) => !x.is_leader)" :key="m.user_id"
              class="flex items-center justify-between gap-3 p-2.5 bg-page rounded-lg">
              <div class="flex items-center gap-2 min-w-0">
                <div class="avatar w-8 h-8 !text-xs">{{ (m.name || '?')[0] }}</div>
                <div class="min-w-0">
                  <span class="text-sm font-medium text-ink-primary">{{ m.name }}</span>
                  <span class="text-xs text-ink-muted ml-2">{{ m.school }} · {{ m.grade }}</span>
                </div>
              </div>
              <button class="text-xs font-medium text-danger hover:underline flex-shrink-0"
                :disabled="removingId === m.user_id" @click="removeMember(m)">
                {{ removingId === m.user_id ? '移除中...' : '移除' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="flex gap-3 mt-8">
        <button class="btn-outline flex-1" @click="showManage = false">取消</button>
        <button class="btn-primary flex-1 py-3" :disabled="saving" @click="saveTeam">{{ saving ? '保存中...' : '保存修改' }}</button>
      </div>
      <div class="mt-6 pt-4 border-t border-line">
        <button class="text-sm text-danger hover:underline" @click="disbandTeam">解散队伍</button>
      </div>
    </Modal>

    <!-- 邀请成员 Modal -->
    <Modal v-model="showInvite" title="邀请成员">
      <div>
        <label for="invite-user-id" class="text-sm font-medium text-ink-primary block mb-1.5">用户 ID</label>
        <input id="invite-user-id" v-model="inviteId" type="number" min="1" class="input-field" placeholder="输入要邀请的用户 ID">
        <p class="text-xs text-ink-muted mt-2">邀请将发送通知给对方，对方接受后自动入队。</p>
      </div>
      <div class="flex gap-3 mt-8">
        <button class="btn-outline flex-1" @click="showInvite = false">取消</button>
        <button class="btn-primary flex-1 py-3" @click="sendInvite">发送邀请</button>
      </div>
    </Modal>
  </div>
</template>
