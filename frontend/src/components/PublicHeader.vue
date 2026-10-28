<script setup>
import BrandMark from './BrandMark.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <header class="public-header">
    <BrandMark />
    <nav aria-label="Main navigation">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
      <RouterLink to="/contact">Contact</RouterLink>
      <RouterLink :to="auth.home || '/login'">{{ auth.home ? 'Dashboard' : 'Log in' }}</RouterLink>
    </nav>
  </header>
</template>

