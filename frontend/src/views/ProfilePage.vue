<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardHeader from '../components/DashboardHeader.vue'
import { useCareSyncStore } from '../stores/careSync'

const route = useRoute()
const router = useRouter()
const store = useCareSyncStore()
const doctor = computed(() => route.meta.role === 'doctor')
const profile = computed(() => (doctor.value ? store.doctorProfile : store.patientProfile))

function save() {
  store.notify('Profile changes saved in this demo session.')
}

function signOut() {
  store.signOut()
  router.push('/login')
}
</script>

<template>
  <main class="dashboard-page profile-page">
    <DashboardHeader :role="doctor ? 'doctor' : 'patient'" />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" :to="doctor ? '/doctor' : '/patient'"
        >Back</RouterLink
      >
    </div>
    <h1>My profile</h1>
    <section class="profile-layout">
      <aside class="profile-summary">
        <img v-if="doctor" :src="store.doctors[0].photo" alt="Dr. Grace Miller" />
        <div v-else class="avatar-initials">U1</div>
        <h2>{{ doctor ? 'Dr. Grace Miller' : 'USER 1' }}</h2>
        <p>{{ doctor ? 'Cardiologist' : 'Patient' }}</p>
        <button class="button button-muted" type="button" @click="signOut">Log out</button>
      </aside>
      <form class="profile-form" @submit.prevent="save">
        <h2>Personal details</h2>
        <div class="profile-fields">
          <label>Full name<input v-model.trim="profile.name" /></label>
          <label v-if="doctor">Specialty<input v-model.trim="profile.specialty" /></label>
          <label v-if="doctor"
            >Licence number<input v-model.trim="profile.licence" placeholder="Registration no."
          /></label>
          <label>Email<input v-model.trim="profile.email" type="email" /></label>
          <label v-if="!doctor">Phone<input v-model.trim="profile.phone" /></label>
          <label v-if="!doctor"
            >Date of birth<input v-model.trim="profile.birthDate" placeholder="DD/MM/YYYY"
          /></label>
        </div>
      </form>
    </section>
    <button class="button button-primary profile-save" type="button" @click="save">
      Save changes
    </button>
    <div v-if="store.lastNotice" class="toast" role="status">{{ store.lastNotice }}</div>
  </main>
</template>
