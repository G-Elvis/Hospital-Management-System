import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler } from './services/apiClient'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// The server timed our session out (or it was never valid): back to the login screen.
setUnauthorizedHandler(() => {
  const auth = useAuthStore()
  if (!auth.user) return // e.g. wrong password on the login form - nothing to expire
  auth.expire()
  router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
})

app.mount('#app')
