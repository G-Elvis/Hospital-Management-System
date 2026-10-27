<script setup>
import mark from '../assets/figma/caresync-mark.png'

defineProps({
  compact: { type: Boolean, default: false },
})
</script>

<template>
  <RouterLink class="brand-mark" to="/" aria-label="CareSync home">
    <img :class="{ compact }" :src="mark" alt="" />
    <span>CARESYNC</span>
  </RouterLink>
</template>
