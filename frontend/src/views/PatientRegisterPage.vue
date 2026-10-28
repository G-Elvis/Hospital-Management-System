<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import DashboardHeader from '../components/DashboardHeader.vue'
import { useClinicStore } from '../stores/clinic'
import { toDateKey } from '../utils/datetime'

const clinic = useClinicStore()
const router = useRouter()

const form = reactive({ full_name: '', date_of_birth: '', gender: '', phone: '', address: '' })
const errors = ref([])
const duplicate = ref('')
const busy = ref(false)
const today = toDateKey(new Date())

async function submit(confirmDuplicate = false) {
  errors.value = []
  duplicate.value = ''
  busy.value = true
  try {
    const patient = await clinic.registerPatient({ ...form }, confirmDuplicate)
    clinic.notify(
      `${patient.full_name} was registered. Choose a doctor and a time to book them in.`,
    )
    router.push({ name: 'appointment-booking', query: { patient: patient.id } })
  } catch (failure) {
    if (failure.status === 409) duplicate.value = failure.message
    else errors.value = failure.errors.length ? failure.errors : [failure.message]
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    await clinic.loadGenders()
  } catch (failure) {
    errors.value = [failure.message]
  }
})
</script>

<template>
  <main class="dashboard-page profile-page">
    <DashboardHeader />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" to="/reception">Back</RouterLink>
    </div>
    <h1>Register a patient</h1>
    <form class="profile-form register-form" @submit.prevent="submit(false)">
      <h2>Patient details</h2>
      <div class="profile-fields">
        <label>Full name<input v-model.trim="form.full_name" required autocomplete="off" /></label>
        <label
          >Date of birth<input v-model="form.date_of_birth" type="date" :max="today" required
        /></label>
        <label
          >Gender
          <select v-model="form.gender" required>
            <option value="" disabled>Select a gender</option>
            <option v-for="gender in clinic.genders" :key="gender" :value="gender">
              {{ gender }}
            </option>
          </select>
        </label>
        <label
          >Phone<input
            v-model.trim="form.phone"
            type="tel"
            required
            placeholder="0712 345 678"
            autocomplete="off"
        /></label>
        <label>Address<input v-model.trim="form.address" autocomplete="off" /></label>
      </div>
      <ul v-if="errors.length" class="form-errors" role="alert">
        <li v-for="message in errors" :key="message">{{ message }}</li>
      </ul>
      <div v-if="duplicate" class="form-warning" role="alert">
        <p>{{ duplicate }}</p>
        <button class="button button-muted" type="button" :disabled="busy" @click="submit(true)">
          Register anyway
        </button>
      </div>
      <button class="button button-primary" type="submit" :disabled="busy">
        {{ busy ? 'Saving…' : 'Register patient' }}
      </button>
    </form>
  </main>
</template>
