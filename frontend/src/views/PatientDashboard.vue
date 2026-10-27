<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import DashboardHeader from '../components/DashboardHeader.vue'
import { useCareSyncStore } from '../stores/careSync'

const store = useCareSyncStore()
const router = useRouter()
const upcomingAppointments = computed(() =>
  store.upcomingAppointments.map((appointment) => ({
    ...appointment,
    doctor: store.doctors.find((doctor) => doctor.id === appointment.doctorId),
  })),
)

function cancel(appointment) {
  store.selectedAppointmentId = appointment.id
  router.push('/appointments/cancel')
}
</script>

<template>
  <main class="dashboard-page">
    <DashboardHeader show-back />
    <section class="service-strip">
      <article>
        <div>
          <h2>Book your appointment</h2>
          <p>Please note this is a paid service</p>
        </div>
        <RouterLink class="button button-muted" to="/appointments/new">Book now</RouterLink>
      </article>
      <article>
        <div>
          <h2>View your Medical Report</h2>
          <p>Lab results / Image reports</p>
          <small>Please note this is a paid service</small>
        </div>
        <RouterLink class="button button-muted" to="/patient/reports">View results</RouterLink>
      </article>
    </section>
    <section class="patient-dashboard-grid">
      <div class="doctor-list">
        <h1>Find your Doctor</h1>
        <p class="subtle-text">(50 specialist)</p>
        <article v-for="doctor in store.doctors" :key="doctor.id" class="doctor-row">
          <img :src="doctor.photo" :alt="doctor.name" />
          <div class="doctor-info">
            <h2>{{ doctor.name }}</h2>
            <p class="subtle-text">{{ doctor.specialty }}</p>
            <p>{{ doctor.description }}</p>
            <RouterLink
              class="button button-muted"
              :to="{ name: 'appointment-booking', query: { doctor: doctor.id } }"
              >Book now</RouterLink
            >
          </div>
        </article>
      </div>
      <aside class="appointments-panel">
        <h2>My appointments</h2>
        <article
          v-for="appointment in upcomingAppointments"
          :key="appointment.id"
          class="appointment-card"
        >
          <img :src="appointment.doctor?.photo" alt="" />
          <div class="appointment-card-person">
            <strong>{{ appointment.doctor?.name }}</strong>
            <span>{{ appointment.doctor?.specialty }}</span>
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
            ><strong>{{ appointment.date }}, {{ appointment.time }}</strong>
          </div>
        </article>
        <p v-if="!upcomingAppointments.length" class="empty-state">No upcoming appointments yet.</p>
      </aside>
    </section>
    <div v-if="store.lastNotice" class="toast" role="status">{{ store.lastNotice }}</div>
  </main>
</template>
