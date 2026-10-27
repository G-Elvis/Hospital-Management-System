<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCareSyncStore } from '../stores/careSync'
import BrandMark from '../components/BrandMark.vue'
import watermark from '../assets/figma/medical-watermark.png'

const route = useRoute()
const router = useRouter()
const store = useCareSyncStore()
const form = reactive({
  firstName: '',
  lastName: '',
  specialty: '',
  licence: '',
  email: '',
  password: '',
})
const page = computed(() => route.meta.page)
const registering = computed(() => page.value.startsWith('register'))
const doctor = ref(page.value === 'register-doctor')
const heading = computed(() => {
  if (page.value === 'forgot-password') return 'Forgot password?'
  if (registering.value) return 'Create an Account'
  return 'Welcome back!'
})

function submit() {
  if (page.value === 'forgot-password') {
    store.notify('If this email is registered, a reset link would be sent. This is a demo.')
    return
  }
  const accountRole = registering.value ? (doctor.value ? 'doctor' : 'patient') : 'patient'
  store.signIn(accountRole)
  router.push(accountRole === 'doctor' ? '/doctor' : '/patient')
}
</script>

<template>
  <main class="auth-page" :style="{ '--watermark': `url(${watermark})` }">
    <BrandMark />
    <RouterLink class="button button-muted auth-back" to="/">Back</RouterLink>
    <form class="auth-card" @submit.prevent="submit">
      <h1>{{ heading }}</h1>
      <template v-if="registering">
        <div class="role-switch">
          <RouterLink :class="{ selected: !doctor }" to="/register" @click="doctor = false"
            >Patient</RouterLink
          >
          <RouterLink :class="{ selected: doctor }" to="/register/doctor" @click="doctor = true"
            >Doctor</RouterLink
          >
        </div>
        <label
          >First name<input v-model.trim="form.firstName" required autocomplete="given-name"
        /></label>
        <label
          >Last name<input v-model.trim="form.lastName" required autocomplete="family-name"
        /></label>
        <label v-if="doctor">Specialty<input v-model.trim="form.specialty" required /></label>
        <label v-if="doctor">Licence number<input v-model.trim="form.licence" required /></label>
      </template>
      <p v-if="page === 'forgot-password'" class="auth-description">
        Enter your email and we will send you a link to reset your password.
      </p>
      <label
        >Email<input v-model.trim="form.email" type="email" required autocomplete="email"
      /></label>
      <label v-if="page === 'login' || registering"
        >Password<input
          v-model="form.password"
          type="password"
          minlength="6"
          required
          :autocomplete="registering ? 'new-password' : 'current-password'"
      /></label>
      <RouterLink
        v-if="page === 'login'"
        class="text-link forgot-link"
        to="/forgot-password"
        >Forgot password?</RouterLink
      >
      <button class="button button-primary auth-submit" type="submit">
        {{
          page === 'forgot-password' ? 'Send reset link' : registering ? 'Create Account' : 'Log in'
        }}
      </button>
      <p v-if="page === 'login'" class="auth-bottom">
        Do not have an account? <RouterLink to="/register">Register</RouterLink>
      </p>
      <p v-if="registering" class="auth-bottom">
        Already have an account? <RouterLink to="/login">Log in</RouterLink>
      </p>
      <RouterLink v-if="page === 'forgot-password'" class="text-link auth-bottom" to="/login"
        >Back to log in</RouterLink
      >
      <p v-if="store.lastNotice" class="inline-notice" role="status">{{ store.lastNotice }}</p>
      <p class="demo-note">
        Demo interface only — no real authentication or password reset is performed.
      </p>
    </form>
  </main>
</template>
