<script setup>
import BrandMark from './BrandMark.vue'
import profileIcon from '../assets/figma/profile-icon.svg'
import { useAuthStore } from '../stores/auth'

defineProps({
  showBack: { type: Boolean, default: false },
})

const auth = useAuthStore()
</script>

<template>
  <header class="dashboard-header">
    <BrandMark compact />
    <div class="welcome-copy">
      <span class="header-divider"></span>
      <strong>Welcome back {{ auth.user?.username }}!</strong>
    </div>
    <RouterLink v-if="showBack" class="button button-muted header-back" to="/">Back</RouterLink>
    <div class="dashboard-actions">
      <RouterLink
        :to="auth.user?.role === 'DOCTOR' ? '/doctor/profile' : '/reception/profile'"
        class="profile-link"
      >
        <img class="dashboard-profile-icon" :src="profileIcon" alt="" />
        <span
          >{{ auth.user?.username }}<small>{{ auth.roleLabel }}</small></span
        >
      </RouterLink>
    </div>
  </header>
</template>
