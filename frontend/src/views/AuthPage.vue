<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BrandMark from '../components/BrandMark.vue'
import watermark from '../assets/figma/medical-watermark.png'
import { ROLE_HOME, useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const error = ref('')
const busy = ref(false)

// Only follow a "?redirect=" that stays inside the app.
function safeRedirect() {
  const target = route.query.redirect
  return typeof target === 'string' && target.startsWith('/') && !target.startsWith('//')
    ? target
    : ''
}

async function submit() {
  error.value = ''
  busy.value = true
  try {
    const user = await auth.login(form.username.trim(), form.password)
    const home = ROLE_HOME[user.role]
    if (!home) {
      await auth.logout()
      error.value = 'Administrator accounts do not have a screen in the web app yet.'
      return
    }
    router.push(safeRedirect() || home)
  } catch (failure) {
    error.value = failure.message
  } finally {
    form.password = ''
    busy.value = false
  }
}
</script>

<template>
  <main class="auth-page" :style="{ '--watermark': `url(${watermark})` }">
    <BrandMark />
    <RouterLink class="button button-muted auth-back" to="/">Back</RouterLink>
    <form class="auth-card" @submit.prevent="submit">
      <h1>Welcome back!</h1>
      <p v-if="auth.notice && !error" class="inline-notice" role="status">{{ auth.notice }}</p>
      <label
        >Username<input
          v-model.trim="form.username"
          required
          autocomplete="username"
          autocapitalize="none"
          spellcheck="false"
      /></label>
      <label
        >Password<input
          v-model="form.password"
          type="password"
          required
          autocomplete="current-password"
      /></label>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="button button-primary auth-submit" type="submit" :disabled="busy">
        {{ busy ? 'Logging in…' : 'Log in' }}
      </button>
      <p class="auth-bottom">Accounts are created by your administrator.</p>
    </form>
  </main>
</template>