<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import DashboardHeader from '../components/DashboardHeader.vue'
import InitialsAvatar from '../components/InitialsAvatar.vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const backTo = computed(() => auth.home || '/')

async function signOut() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <main class="dashboard-page profile-page">
    <DashboardHeader />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" :to="backTo">Back</RouterLink>
    </div>
    <h1>My profile</h1>
    <section class="profile-layout">
      <aside class="profile-summary">
        <InitialsAvatar :name="auth.user?.username" :size="142" />
        <h2>{{ auth.user?.username }}</h2>
        <p>{{ auth.roleLabel }}</p>
        <button class="button button-muted" type="button" @click="signOut">Log out</button>
      </aside>
      <div class="profile-form">
        <h2>Account details</h2>
        <div class="profile-fields">
          <label>Username<input :value="auth.user?.username" readonly /></label>
          <label>Role<input :value="auth.roleLabel" readonly /></label>
        </div>
        <p class="subtle-text">Account details are managed by an administrator.</p>
      </div>
    </section>
  </main>
</template>
