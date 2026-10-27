<script setup>
import BrandMark from './BrandMark.vue'
import profileIcon from '../assets/figma/profile-icon.svg'
import chatIcon from '../assets/figma/chat-icon.svg'

defineProps({
  role: { type: String, default: 'patient' },
  showBack: { type: Boolean, default: false },
})
</script>

<template>
  <header class="dashboard-header">
    <BrandMark compact />
    <div class="welcome-copy">
      <span class="header-divider"></span>
      <strong>Welcome back {{ role === 'doctor' ? 'Doctor, Miller' : 'user' }}!</strong>
    </div>
    <RouterLink v-if="showBack" class="button button-muted header-back" to="/">Back</RouterLink>
    <div class="dashboard-actions">
      <RouterLink
        :to="role === 'doctor' ? '/doctor/profile' : '/patient/profile'"
        class="profile-link"
      >
        <img class="dashboard-profile-icon" :src="profileIcon" alt="" />
        <span
          >{{ role === 'doctor' ? 'Dr. Miller' : 'USER 1' }}<small>{{ role }}</small></span
        >
      </RouterLink>
      <RouterLink
        v-if="role === 'doctor'"
        class="chat-link"
        to="/doctor/chat"
        aria-label="Open messages"
      >
        <img :src="chatIcon" alt="" />
      </RouterLink>
    </div>
  </header>
</template>
