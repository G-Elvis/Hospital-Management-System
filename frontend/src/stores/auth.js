import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { api, refreshSession, setCsrfToken } from '../services/apiClient'

// Roles come from the backend (app/domain/user.py). Reception staff book and cancel
// appointments and register patients; doctors manage their own appointments and records.
// Administrators have no screens in the web app yet.
export const ROLE_HOME = { RECEPTIONIST: '/reception', DOCTOR: '/doctor' }
export const ROLE_LABEL = { RECEPTIONIST: 'Receptionist', DOCTOR: 'Doctor', ADMIN: 'Administrator' }

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const ready = ref(false)
  const notice = ref('')
  let starting = null

  const home = computed(() => (user.value ? ROLE_HOME[user.value.role] || null : null))
  const roleLabel = computed(() => (user.value ? ROLE_LABEL[user.value.role] : ''))

  function apply(payload) {
    setCsrfToken(payload.csrf_token)
    user.value = payload.user
  }

  /** Restore the session once (a page refresh keeps the user logged in via the cookie). */
  function init() {
    starting ??= refreshSession()
      .then(apply)
      .catch(() => {
        user.value = null // server unreachable: the login screen will say so
      })
      .finally(() => {
        ready.value = true
      })
    return starting
  }

  async function login(username, password) {
    const payload = await api.post('login', { username, password })
    apply(payload)
    notice.value = ''
    return payload.user
  }

  async function logout() {
    try {
      apply(await api.post('logout'))
    } finally {
      user.value = null
    }
  }

  /** The server says we are no longer logged in (the 15-minute inactivity timeout). */
  function expire() {
    user.value = null
    notice.value = 'Your session has ended. Please log in again.'
  }

  return { user, ready, notice, home, roleLabel, init, login, logout, expire }
})
