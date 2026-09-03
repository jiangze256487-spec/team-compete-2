<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { grades } from '@/constants/tags'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const authPage = ref('login')
const loading = ref(false)

const loginForm = ref({ student_id: '', password: '' })
const regForm = ref({ student_id: '', name: '', school: '', major: '', grade: '', password: '', confirm: '' })

const loginErrors = reactive({ student_id: '', password: '' })
const regErrors = reactive({ student_id: '', name: '', password: '', confirm: '' })

function validStudentId(v) {
  return typeof v === 'string' && v.trim().length >= 4
}

async function handleLogin() {
  loginErrors.student_id = ''
  loginErrors.password = ''
  let invalid = false
  if (!loginForm.value.student_id) {
    loginErrors.student_id = '请输入学号'
    invalid = true
  } else if (!validStudentId(loginForm.value.student_id)) {
    loginErrors.student_id = '学号格式不正确'
    invalid = true
  }
  if (!loginForm.value.password) {
    loginErrors.password = '请输入密码'
    invalid = true
  }
  if (invalid) return

  loading.value = true
  try {
    await auth.login({ student_id: loginForm.value.student_id.trim(), password: loginForm.value.password })
    router.push('/')
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    loading.value = false
  }
}

function validateRegister() {
  regErrors.student_id = ''
  regErrors.name = ''
  regErrors.password = ''
  regErrors.confirm = ''
  let invalid = false

  if (!regForm.value.student_id) {
    regErrors.student_id = '请输入学号'
    invalid = true
  } else if (!validStudentId(regForm.value.student_id)) {
    regErrors.student_id = '学号格式不正确（至少 4 位）'
    invalid = true
  }
  if (!regForm.value.name) {
    regErrors.name = '请输入姓名'
    invalid = true
  }
  if (!regForm.value.password) {
    regErrors.password = '请设置密码'
    invalid = true
  } else if (regForm.value.password.length < 6) {
    regErrors.password = '密码至少 6 位'
    invalid = true
  }
  if (!regForm.value.confirm) {
    regErrors.confirm = '请再次输入密码'
    invalid = true
  } else if (regForm.value.confirm !== regForm.value.password) {
    regErrors.confirm = '两次输入的密码不一致'
    invalid = true
  }
  return !invalid
}

async function handleRegister() {
  if (!validateRegister()) return
  loading.value = true
  try {
    await auth.register({
      student_id: regForm.value.student_id.trim(),
      name: regForm.value.name.trim(),
      school: regForm.value.school.trim(),
      major: regForm.value.major.trim(),
      grade: regForm.value.grade,
      password: regForm.value.password
    })
    router.push('/')
  } catch (e) {
    toast.show(e, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#EEF2FF] via-[#FAF5FF] to-[#F8FAFC] p-4">

    <!-- Login -->
    <div v-if="authPage === 'login'" class="card p-10 w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl gradient-brand mx-auto mb-4 flex items-center justify-center">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        </div>
        <h2 class="text-2xl font-bold text-ink-primary">欢迎回来</h2>
        <p class="text-ink-secondary text-sm mt-1">登录你的竞赛组队账号</p>
      </div>
      <div class="space-y-4">
        <div>
          <label for="login-student-id" class="text-sm font-medium text-ink-primary block mb-1.5">学号</label>
          <input id="login-student-id" v-model="loginForm.student_id" type="text" class="input-field" placeholder="请输入学号" :class="{ 'border-danger': loginErrors.student_id }">
          <p v-if="loginErrors.student_id" class="text-xs text-danger mt-1">{{ loginErrors.student_id }}</p>
        </div>
        <div>
          <label for="login-password" class="text-sm font-medium text-ink-primary block mb-1.5">密码</label>
          <input id="login-password" v-model="loginForm.password" type="password" class="input-field" placeholder="请输入密码" :class="{ 'border-danger': loginErrors.password }" @keyup.enter="handleLogin">
          <p v-if="loginErrors.password" class="text-xs text-danger mt-1">{{ loginErrors.password }}</p>
        </div>
        <button class="btn-primary w-full py-3 text-base" :disabled="loading" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</button>
      </div>
      <p class="text-center text-sm text-ink-secondary mt-6">
        还没有账号？<span class="text-primary font-medium cursor-pointer hover:underline" @click="authPage = 'register'">学号注册</span>
      </p>
    </div>

    <!-- Register -->
    <div v-else class="card p-10 w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl gradient-brand mx-auto mb-4 flex items-center justify-center">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/></svg>
        </div>
        <h2 class="text-2xl font-bold text-ink-primary">学号注册</h2>
        <p class="text-ink-secondary text-sm mt-1">创建账号开始组队之旅</p>
      </div>
      <div class="space-y-4">
        <div>
          <label for="reg-student-id" class="text-sm font-medium text-ink-primary block mb-1.5">学号</label>
          <input id="reg-student-id" v-model="regForm.student_id" type="text" class="input-field" placeholder="请输入学号" :class="{ 'border-danger': regErrors.student_id }">
          <p v-if="regErrors.student_id" class="text-xs text-danger mt-1">{{ regErrors.student_id }}</p>
        </div>
        <div>
          <label for="reg-name" class="text-sm font-medium text-ink-primary block mb-1.5">姓名</label>
          <input id="reg-name" v-model="regForm.name" type="text" class="input-field" placeholder="请输入真实姓名" :class="{ 'border-danger': regErrors.name }">
          <p v-if="regErrors.name" class="text-xs text-danger mt-1">{{ regErrors.name }}</p>
        </div>
        <div>
          <label for="reg-school" class="text-sm font-medium text-ink-primary block mb-1.5">学校</label>
          <input id="reg-school" v-model="regForm.school" type="text" class="input-field" placeholder="请输入学校名称">
        </div>
        <div>
          <label for="reg-major" class="text-sm font-medium text-ink-primary block mb-1.5">专业</label>
          <input id="reg-major" v-model="regForm.major" type="text" class="input-field" placeholder="请输入专业">
        </div>
        <div>
          <label for="reg-grade" class="text-sm font-medium text-ink-primary block mb-1.5">年级</label>
          <select id="reg-grade" v-model="regForm.grade" class="input-field">
            <option value="">请选择年级</option>
            <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>
        <div>
          <label for="reg-password" class="text-sm font-medium text-ink-primary block mb-1.5">密码</label>
          <input id="reg-password" v-model="regForm.password" type="password" class="input-field" placeholder="请设置密码（至少6位）" :class="{ 'border-danger': regErrors.password }">
          <p v-if="regErrors.password" class="text-xs text-danger mt-1">{{ regErrors.password }}</p>
        </div>
        <div>
          <label for="reg-confirm" class="text-sm font-medium text-ink-primary block mb-1.5">确认密码</label>
          <input id="reg-confirm" v-model="regForm.confirm" type="password" class="input-field" placeholder="请再次输入密码" :class="{ 'border-danger': regErrors.confirm }" @keyup.enter="handleRegister">
          <p v-if="regErrors.confirm" class="text-xs text-danger mt-1">{{ regErrors.confirm }}</p>
        </div>
        <button class="btn-primary w-full py-3 text-base" :disabled="loading" @click="handleRegister">{{ loading ? '注册中...' : '注 册' }}</button>
      </div>
      <p class="text-center text-sm text-ink-secondary mt-6">
        已有账号？<span class="text-primary font-medium cursor-pointer hover:underline" @click="authPage = 'login'">去登录</span>
      </p>
    </div>
  </div>
</template>
