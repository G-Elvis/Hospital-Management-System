<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import DashboardHeader from '../components/DashboardHeader.vue'
import InitialsAvatar from '../components/InitialsAvatar.vue'
import { useClinicStore } from '../stores/clinic'
import { formatDate, formatTime } from '../utils/datetime'

const clinic = useClinicStore()

const statusFilters = ['All', 'Scheduled', 'Completed', 'Cancelled']
const activeFilter = ref('Scheduled')
const filterDate = ref('')
const loading = ref(true)
const loadError = ref('')
const actionError = ref('')

// The server only returns this doctor's own appointments.
const appointments = computed(() =>
  clinic.appointments
    .filter((item) => activeFilter.value === 'All' || item.status === activeFilter.value)
    .filter((item) => !filterDate.value || item.dateKey === filterDate.value)
    .sort((a, b) => `${a.dateKey} ${a.time}`.localeCompare(`${b.dateKey} ${b.time}`)),
)

async function complete(appointment) {
  if (!window.confirm(`Mark ${appointment.patientName}'s appointment as completed?`)) return
  actionError.value = ''
  try {
    await clinic.completeAppointment(appointment.id)
    clinic.notify('Appointment marked as completed.')
  } catch (failure) {
    actionError.value = failure.message
  }
}

// ---- patient finder (opens a patient's medical history) --------------------------------
const patientQuery = ref('')
const patientResults = ref([])
const searched = ref(false)
let searchTimer

async function searchPatients() {
  try {
    patientResults.value = await clinic.searchPatients(patientQuery.value)
    searched.value = true
  } catch (failure) {
    actionError.value = failure.message
  }
}

watch(patientQuery, () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(searchPatients, 250)
})
onBeforeUnmount(() => window.clearTimeout(searchTimer))

onMounted(async () => {
  try {
    await clinic.loadAppointments()
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
    <h1 class="page-section-title">Doctor dashboard</h1>
    <section class="doctor-management">
      <div class="management-heading">
        <div>
          <h2>Appointment Management</h2>
          <p>Review your appointments and complete them once the patient has been seen.</p>
        </div>
        <div class="appointment-filters">
          <label>
            Date
            <input v-model="filterDate" type="date" />
          </label>
          <label>
            Status
            <select v-model="activeFilter">
              <option v-for="status in statusFilters" :key="status" :value="status">
                {{ status }}
              </option>
            </select>
          </label>
        </div>
      </div>
      <p v-if="loadError || actionError" class="form-error" role="alert">
        {{ loadError || actionError }}
      </p>
      <div class="doctor-management-grid">
        <div class="doctor-appointment-list">
          <article
            v-for="appointment in appointments"
            :key="appointment.id"
            class="doctor-appointment-card"
          >
            <div class="doctor-appointment-patient">
              <InitialsAvatar :name="appointment.patientName" :size="54" />
              <div>
                <h3>{{ appointment.patientName }}</h3>
                <p>Patient ID {{ appointment.patientId }}</p>
              </div>
            </div>
            <div class="doctor-appointment-info">
              <strong>{{ formatDate(appointment.dateKey) }}</strong>
              <span>{{ formatTime(appointment.time) }}</span>
              <span
                class="appointment-status"
                :class="`status-${appointment.status.toLowerCase()}`"
              >
                {{ appointment.status }}
              </span>
            </div>
            <div class="appointment-actions">
              <RouterLink
                class="button button-muted"
                :to="{ name: 'patient-history', params: { id: appointment.patientId } }"
                >Medical history</RouterLink
              >
              <button
                v-if="appointment.status === 'Scheduled'"
                class="button button-primary"
                type="button"
                @click="complete(appointment)"
              >
                Complete
              </button>
            </div>
          </article>
          <p v-if="loading" class="empty-state">Loading…</p>
          <p v-else-if="!appointments.length && !loadError" class="empty-state">
            No appointments match these filters.
          </p>
        </div>
        <aside class="doctor-dash-side">
          <section class="patient-finder">
            <h2>Find a patient</h2>
            <label class="sr-only" for="patient-finder-input">Search patients</label>
            <input
              id="patient-finder-input"
              v-model="patientQuery"
              type="search"
              placeholder="Name, phone number or ID"
              autocomplete="off"
            />
            <RouterLink
              v-for="patient in patientResults"
              :key="patient.id"
              class="button button-muted wide-button"
              :to="{ name: 'patient-history', params: { id: patient.id } }"
              >{{ patient.full_name }}</RouterLink
            >
            <p v-if="searched && !patientResults.length" class="empty-state">No patients found.</p>
          </section>
        </aside>
      </div>
    </section>
    <div v-if="clinic.notice" class="toast" role="status">{{ clinic.notice }}</div>
  </main>
</template>
