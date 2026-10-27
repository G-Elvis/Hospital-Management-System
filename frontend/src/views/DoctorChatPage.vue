<script setup>
import { computed, ref } from 'vue'
import DashboardHeader from '../components/DashboardHeader.vue'
import { useCareSyncStore } from '../stores/careSync'

const store = useCareSyncStore()
const draft = ref('')
const activeContact = computed(() => store.messages[store.activeChat] ?? store.messages[0])

function send() {
  if (store.sendMessage(draft.value)) draft.value = ''
}
</script>

<template>
  <main class="dashboard-page chat-page">
    <DashboardHeader role="doctor" />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" to="/doctor">Back</RouterLink>
    </div>
    <section class="chat-layout">
      <aside class="chat-contacts">
        <h2>Messages</h2>
        <button
          v-for="(message, index) in store.messages"
          :key="message.contact"
          type="button"
          class="contact-item"
          :class="{ active: store.activeChat === index }"
          @click="store.activeChat = index"
        >
          <img :src="message.photo" :alt="message.contact" />
          <span
            ><strong>{{ message.contact }}</strong
            ><small>{{ message.text }}</small></span
          ><time>{{ message.time }}</time>
        </button>
      </aside>
      <section class="conversation">
        <header class="conversation-header">
          <img :src="activeContact?.photo" :alt="activeContact?.contact" />
          <div>
            <h2>{{ activeContact?.contact }}</h2>
            <p>Initial visit</p>
          </div>
        </header>
        <div class="conversation-messages" aria-live="polite">
          <div
            v-for="message in store.chatMessages"
            :key="message.id"
            class="chat-message"
            :class="message.from"
          >
            <p>{{ message.text }}</p>
            <time>{{ message.time }}</time>
          </div>
        </div>
        <form class="message-composer" @submit.prevent="send">
          <label class="sr-only" for="chat-message">Type a message</label>
          <input id="chat-message" v-model="draft" placeholder="Type a message" />
          <button class="button button-primary" type="submit">Send</button>
        </form>
      </section>
    </section>
  </main>
</template>
