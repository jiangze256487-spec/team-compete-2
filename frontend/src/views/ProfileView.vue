<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import Modal from '@/components/Modal.vue'

const auth = useAuthStore()
const toast = useToastStore()

const allSkillTags = ['Python', 'Java', 'C++', '前端', '后端', '算法', '机器学习', '数据分析', 'UI设计', '产品策划', '文案', '项目管理']
const allAttrTags = ['大一', '大二', '大三', '大四', '研一', '研二', '研三', '计算机', '数学', '经管', '设计', '周末有空', '周中有空']

const user = ref(auth.user || {})
const loading = ref(true)

const editingTags = ref(false)
const savingTags = ref(false)
const tagDraft = ref({ skills: [], attrs: [] })

async function load() {
  loading.value = true
  try {
    user.value = await auth.fetchMe()
  } catch (e) {
    toast.show(e)
  } finally {
    loading.value = false
  }
}

function openTagEditor() {
  tagDraft.value = { skills: [...(user.value.skills || [])], attrs: [...(user.value.attrs || [])] }
  editingTags.value = true
}

function toggle(listKey, tag) {
  const idx = tagDraft.value[listKey].indexOf(tag)
  if (idx >= 0) tagDraft.value[listKey].splice(idx, 1)
  else tagDraft.value[listKey].push(tag)
}

async function saveTags() {
  savingTags.value = true
  try {
    const updated = await authApi.updateTags(tagDraft.value)
    auth.updateUser(updated)
    user.value = updated
    editingTags.value = false
    toast.show('标签已更新')
  } catch (e) {
    toast.show(e)
  } finally {
    savingTags.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="p-8 max-w-4xl">
    <h1 class="text-2xl font-bold text-ink-primary mb-8">个人中心</h1>

    <!-- Profile Card -->
    <div class="card p-8 mb-8">
      <div v-if="loading" class="space-y-3">
        <div class="skeleton h-16 w-16 rounded-full"></div>
        <div class="skeleton h-5 w-40"></div>
        <div class="skeleton h-24"></div>
      </div>
      <template v-else>
        <div class="flex items-center gap-5 mb-6">
          <div class="avatar avatar-lg">{{ (user.name || '?')[0] }}</div>
          <div>
            <h2 class="text-xl font-bold text-ink-primary">{{ user.name }}</h2>
            <p class="text-sm text-ink-secondary">{{ user.school }} · {{ user.major }} · {{ user.grade }}</p>
            <p class="text-xs text-ink-muted mt-0.5">学号：{{ user.student_id }}</p>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4 p-4 bg-page rounded-xl mb-6">
          <div class="text-center"><div class="text-xl font-bold text-primary">{{ (user.attrs || []).length }}</div><div class="text-xs text-ink-muted">专业属性</div></div>
          <div class="text-center border-x border-line"><div class="text-xl font-bold text-accent">{{ (user.skills || []).length }}</div><div class="text-xs text-ink-muted">技能标签</div></div>
          <div class="text-center"><div class="text-xl font-bold text-cta">—</div><div class="text-xs text-ink-muted">综合评分</div></div>
        </div>

        <div class="mb-6">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-ink-primary">技能标签</h3>
            <button class="text-sm text-primary font-medium hover:underline" @click="openTagEditor">修改标签</button>
          </div>
          <div class="flex flex-wrap gap-2">
            <span v-for="t in (user.skills || [])" :key="t" class="tag tag-indigo text-sm">{{ t }}</span>
            <span v-if="!(user.skills || []).length" class="text-sm text-ink-muted">暂无技能标签</span>
          </div>
        </div>

        <div>
          <h3 class="font-semibold text-ink-primary mb-3">专业属性</h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="t in (user.attrs || [])" :key="t" class="tag tag-purple text-sm">{{ t }}</span>
            <span v-if="!(user.attrs || []).length" class="text-sm text-ink-muted">暂无专业属性</span>
          </div>
        </div>
      </template>
    </div>

    <!-- Edit Tags Modal -->
    <Modal v-model="editingTags" title="修改标签">
      <div>
        <label class="text-sm font-medium text-ink-primary block mb-3">选择你的技能标签</label>
        <div class="flex flex-wrap gap-2 mb-4">
          <span v-for="t in allSkillTags" :key="t" class="tag cursor-pointer text-sm py-1.5 px-4"
            :class="tagDraft.skills.includes(t) ? 'tag-indigo' : 'tag-gray'" @click="toggle('skills', t)">{{ t }}</span>
        </div>
        <label class="text-sm font-medium text-ink-primary block mb-3">专业属性</label>
        <div class="flex flex-wrap gap-2">
          <span v-for="t in allAttrTags" :key="t" class="tag cursor-pointer text-sm py-1.5 px-4"
            :class="tagDraft.attrs.includes(t) ? 'tag-purple' : 'tag-gray'" @click="toggle('attrs', t)">{{ t }}</span>
        </div>
      </div>
      <div class="flex gap-3 mt-8">
        <button class="btn-outline flex-1" @click="editingTags = false">取消</button>
        <button class="btn-primary flex-1 py-3" :disabled="savingTags" @click="saveTags">保存</button>
      </div>
    </Modal>
  </div>
</template>
