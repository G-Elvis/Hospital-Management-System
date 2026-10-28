<script setup>
import { computed } from 'vue'
import { initialsOf } from '../utils/datetime'

// The API has names, not photos, so people are shown as initials.
const props = defineProps({
  name: { type: String, default: '' },
  size: { type: Number, default: 54 },
  square: { type: Boolean, default: false },
})
const initials = computed(() => initialsOf(props.name))
</script>

<template>
  <span
    class="initials-avatar"
    :class="{ 'initials-avatar-square': square }"
    :style="{ '--avatar-size': `${size}px` }"
    role="img"
    :aria-label="name"
    >{{ initials }}</span
  >
</template>
