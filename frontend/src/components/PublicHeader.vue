<script setup>
import BrandMark from './BrandMark.vue'
</script>

<template>
  <header class="public-header">
    <BrandMark />
    <nav aria-label="Main navigation">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
      <RouterLink to="/contact">Contact</RouterLink>
      <RouterLink to="/login">Log in</RouterLink>
    </nav>
  </header>
</template>
