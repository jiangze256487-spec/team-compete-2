<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { allSkillTags, allAttrTags, allTimeTags } from '@/constants/tags'
import Modal from '@/components/Modal.vue'

const auth = useAuthStore()
const toast = useToastStore()

const user = ref(auth.user || {})
const loading = ref(true)

const editingTags = ref(false)
const savingTags = ref(false)
const tagDraft = ref({ skills: [], attrs: [], times: [] })

async function load() {
  loading.value = true
  try {
    user.value = await auth.fetchMe()
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    loading.value = false
  }
}

function openTagEditor() {
  const allAttrs = user.value.attrs || []
  tagDraft.value = {
    skills: [...(user.value.skills || [])],
    attrs: allAttrs.filter((t) => allAttrTags.includes(t)),
    times: allAttrs.filter((t) => allTimeTags.includes(t))
  }
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
    const updated = await authApi.updateTags({
      skills: tagDraft.value.skills,
      attrs: [...tagDraft.value.attrs, ...tagDraft.value.times]
    })
    auth.updateUser(updated)
    user.value = updated
    editingTags.value = false
    toast.show('标签已更新')
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    savingTags.value = false
  }
}

// ===== 编辑资料 =====
const showEditProfile = ref(false)
const savingProfile = ref(false)
const profileForm = ref({ name: '', school: '', major: '', grade: '', phone: '' })

function openEditProfile() {
  profileForm.value = {
    name: user.value.name || '',
    school: user.value.school || '',
    major: user.value.major || '',
    grade: user.value.grade || '',
    phone: user.value.phone || ''
  }
  showEditProfile.value = true
}

async function saveProfile() {
  if (!profileForm.value.name) {
    toast.show('姓名不能为空', 'warning')
    return
  }
  savingProfile.value = true
  try {
    const updated = await authApi.updateMe(profileForm.value)
    auth.updateUser(updated)
    user.value = updated
    showEditProfile.value = false
    toast.show('资料已更新')
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    savingProfile.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="p-4 md:p-8 max-w-4xl">
    <h1 class="text-2xl font-bold text-ink-primary mb-8">个人中心</h1>

    <!-- Profile Card -->
    <div class="card p-8 mb-8">
      <div v-if="loading" class="space-y-3">
        <div class="skeleton h-16 w-16 rounded-full"></div>
        <div class="skeleton h-5 w-40"></div>
        <div class="skeleton h-24"></div>
      </div>
      <template v-else>
        <div class="flex items-start gap-5 mb-6 flex-wrap">
          <div class="avatar avatar-lg">{{ (user.name || '?')[0] }}</div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-3 flex-wrap">
              <h2 class="text-xl font-bold text-ink-primary">{{ user.name }}</h2>
              <button class="text-sm text-primary font-medium hover:underline" @click="openEditProfile">编辑资料</button>
            </div>
            <p class="text-sm text-ink-secondary mt-1">{{ user.school }} · {{ user.major }} · {{ user.grade }}</p>
            <p class="text-xs text-ink-muted mt-0.5">学号：{{ user.student_id }}<span v-if="user.phone"> · 电话：{{ user.phone }}</span></p>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4 p-4 bg-page rounded-xl mb-6">
          <div class="text-center"><div class="text-xl font-bold text-primary">{{ (user.attrs || []).length }}</div><div class="text-xs text-ink-muted">专业属性</div></div>
          <div class="text-center border-l border-line"><div class="text-xl font-bold text-accent">{{ (user.skills || []).length }}</div><div class="text-xs text-ink-muted">技能标签</div></div>
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

    <!-- Edit Profile Modal -->
    <Modal v-model="showEditProfile" title="编辑资料">
      <div class="space-y-4">
        <div>
          <label for="pf-name" class="text-sm font-medium text-ink-primary block mb-1.5">姓名</label>
          <input id="pf-name" v-model="profileForm.name" type="text" maxlength="64" class="input-field">
        </div>
        <div>
          <label for="pf-school" class="text-sm font-medium text-ink-primary block mb-1.5">学校</label>
          <input id="pf-school" v-model="profileForm.school" type="text" maxlength="128" class="input-field">
        </div>
        <div>
          <label for="pf-major" class="text-sm font-medium text-ink-primary block mb-1.5">专业</label>
          <input id="pf-major" v-model="profileForm.major" type="text" maxlength="64" class="input-field">
        </div>
        <div>
          <label for="pf-grade" class="text-sm font-medium text-ink-primary block mb-1.5">年级</label>
          <select id="pf-grade" v-model="profileForm.grade" class="input-field">
            <option value="">请选择年级</option>
            <option v-for="g in ['大一', '大二', '大三', '大四', '研一', '研二', '研三']" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>
        <div>
          <label for="pf-phone" class="text-sm font-medium text-ink-primary block mb-1.5">联系电话</label>
          <input id="pf-phone" v-model="profileForm.phone" type="text" maxlength="20" class="input-field" placeholder="请输入手机号/微信">
          <p class="text-xs text-ink-muted mt-1">仅同队成员（入队后）可见</p>
        </div>
      </div>
      <div class="flex gap-3 mt-8">
        <button class="btn-outline flex-1" @click="showEditProfile = false">取消</button>
        <button class="btn-primary flex-1 py-3" :disabled="savingProfile" @click="saveProfile">{{ savingProfile ? '保存中...' : '保存' }}</button>
      </div>
    </Modal>

    <!-- Edit Tags Modal -->
    <Modal v-model="editingTags" title="修改标签">
      <div>
        <label class="text-sm font-medium text-ink-primary block mb-3">选择你的技能标签</label>
        <div class="flex flex-wrap gap-2 mb-4">
          <span v-for="t in allSkillTags" :key="t" class="tag cursor-pointer text-sm py-1.5 px-4"
            :class="tagDraft.skills.includes(t) ? 'tag-indigo' : 'tag-gray'" @click="toggle('skills', t)">{{ t }}</span>
        </div>
        <label class="text-sm font-medium text-ink-primary block mb-3">专业属性</label>
        <div class="flex flex-wrap gap-2 mb-4">
          <span v-for="t in allAttrTags" :key="t" class="tag cursor-pointer text-sm py-1.5 px-4"
            :class="tagDraft.attrs.includes(t) ? 'tag-purple' : 'tag-gray'" @click="toggle('attrs', t)">{{ t }}</span>
        </div>
        <label class="text-sm font-medium text-ink-primary block mb-3">可用时间</label>
        <div class="flex flex-wrap gap-2">
          <span v-for="t in allTimeTags" :key="t" class="tag cursor-pointer text-sm py-1.5 px-4"
            :class="tagDraft.times.includes(t) ? 'tag-purple' : 'tag-gray'" @click="toggle('times', t)">{{ t }}</span>
        </div>
      </div>
      <div class="flex gap-3 mt-8">
        <button class="btn-outline flex-1" @click="editingTags = false">取消</button>
        <button class="btn-primary flex-1 py-3" :disabled="savingTags" @click="saveTags">保存</button>
      </div>
    </Modal>
  </div>
</template>
