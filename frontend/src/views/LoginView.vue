<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const authPage = ref('login')
const loading = ref(false)

const loginForm = ref({ student_id: '', password: '' })
const regForm = ref({ student_id: '', name: '', school: '', major: '', grade: '', password: '' })
const grades = ['大一', '大二', '大三', '大四', '研一', '研二', '研三']

async function handleLogin() {
  if (!loginForm.value.student_id || !loginForm.value.password) {
    toast.show('请输入学号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(loginForm.value)
    router.push('/')
  } catch (e) {
    toast.show(e)
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!regForm.value.student_id || !regForm.value.name || !regForm.value.password) {
    toast.show('请填写学号、姓名和密码')
    return
  }
  if (regForm.value.password.length < 6) {
    toast.show('密码至少 6 位')
    return
  }
  loading.value = true
  try {
    await auth.register(regForm.value)
    router.push('/')
  } catch (e) {
    toast.show(e)
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
          <label class="text-sm font-medium text-ink-primary block mb-1.5">学号</label>
          <input v-model="loginForm.student_id" type="text" class="input-field" placeholder="请输入学号">
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">密码</label>
          <input v-model="loginForm.password" type="password" class="input-field" placeholder="请输入密码" @keyup.enter="handleLogin">
        </div>
        <button class="btn-primary w-full py-3 text-base" :disabled="loading" @click="handleLogin">登 录</button>
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
          <label class="text-sm font-medium text-ink-primary block mb-1.5">学号</label>
          <input v-model="regForm.student_id" type="text" class="input-field" placeholder="请输入学号">
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">姓名</label>
          <input v-model="regForm.name" type="text" class="input-field" placeholder="请输入真实姓名">
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">学校</label>
          <input v-model="regForm.school" type="text" class="input-field" placeholder="请输入学校名称">
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">专业</label>
          <input v-model="regForm.major" type="text" class="input-field" placeholder="请输入专业">
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">年级</label>
          <select v-model="regForm.grade" class="input-field">
            <option value="">请选择年级</option>
            <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-medium text-ink-primary block mb-1.5">密码</label>
          <input v-model="regForm.password" type="password" class="input-field" placeholder="请设置密码（至少6位）">
        </div>
        <button class="btn-primary w-full py-3 text-base" :disabled="loading" @click="handleRegister">注 册</button>
      </div>
      <p class="text-center text-sm text-ink-secondary mt-6">
        已有账号？<span class="text-primary font-medium cursor-pointer hover:underline" @click="authPage = 'login'">去登录</span>
      </p>
    </div>
  </div>
</template>
