<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import DashboardHeader from '../components/DashboardHeader.vue'
import InitialsAvatar from '../components/InitialsAvatar.vue'
import { useClinicStore } from '../stores/clinic'
import { formatDate, formatTime } from '../utils/datetime'

const clinic = useClinicStore()
const router = useRouter()
const loading = ref(true)
const loadError = ref('')

const upcoming = computed(() =>
  clinic.appointments
    .filter((item) => item.status === 'Scheduled')
    .sort((a, b) => `${a.dateKey} ${a.time}`.localeCompare(`${b.dateKey} ${b.time}`)),
)

function upcomingCount(doctorId) {
  return upcoming.value.filter((item) => item.doctorId === doctorId).length
}

function cancel(appointment) {
  router.push({ name: 'appointment-cancel', query: { id: appointment.id } })
}

onMounted(async () => {
  try {
    await Promise.all([clinic.loadDoctors(), clinic.loadAppointments()])
  } catch (failure) {
    loadError.value = failure.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="dashboard-page">
    <DashboardHeader show-back />
    <section class="service-strip">
      <article>
        <div>
          <h2>Book an appointment</h2>
          <p>Choose a patient, a doctor and a time slot</p>
        </div>
        <RouterLink class="button button-muted" to="/appointments/new">Book now</RouterLink>
      </article>
      <article>
        <div>
          <h2>Register a patient</h2>
          <p>Add a new patient to the clinic records</p>
        </div>
        <RouterLink class="button button-muted" to="/reception/patients/new">Register</RouterLink>
      </article>
    </section>
    <p v-if="loadError" class="form-error" role="alert">{{ loadError }}</p>
    <section class="patient-dashboard-grid">
      <div class="doctor-list">
        <h1>Our doctors</h1>
        <p class="subtle-text">({{ clinic.doctors.length }} available)</p>
        <article v-for="doctor in clinic.doctors" :key="doctor.id" class="doctor-row">
          <InitialsAvatar :name="doctor.username" :size="132" />
          <div class="doctor-info">
            <h2>{{ doctor.username }}</h2>
            <p class="subtle-text">Doctor</p>
            <p>
              {{ upcomingCount(doctor.id) }} upcoming
              {{ upcomingCount(doctor.id) === 1 ? 'appointment' : 'appointments' }}
            </p>
            <RouterLink
              class="button button-muted"
              :to="{ name: 'appointment-booking', query: { doctor: doctor.id } }"
              >Book now</RouterLink
            >
          </div>
        </article>
        <p v-if="!loading && !clinic.doctors.length && !loadError" class="empty-state">
          No doctors have been added yet. An administrator can create doctor accounts.
        </p>
      </div>
      <aside class="appointments-panel">
        <h2>Upcoming appointments</h2>
        <article v-for="appointment in upcoming" :key="appointment.id" class="appointment-card">
          <InitialsAvatar :name="appointment.patientName" :size="62" />
          <div class="appointment-card-person">
            <strong>{{ appointment.patientName }}</strong>
            <span>with {{ appointment.doctorName }}</span>
          </div>
          <button
            class="button button-muted danger-button"
            type="button"
            @click="cancel(appointment)"
          >
            Cancel
          </button>
          <div class="appointment-date">
            <small>Date &amp; Time</small
            ><strong
              >{{ formatDate(appointment.dateKey) }}, {{ formatTime(appointment.time) }}</strong
            >
          </div>
        </article>
        <p v-if="loading" class="empty-state">Loading…</p>
        <p v-else-if="!upcoming.length" class="empty-state">No upcoming appointments yet.</p>
      </aside>
    </section>
    <div v-if="clinic.notice" class="toast" role="status">{{ clinic.notice }}</div>
  </main>
</template>
