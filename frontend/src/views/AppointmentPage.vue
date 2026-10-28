<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BrandMark from '../components/BrandMark.vue'
import DashboardHeader from '../components/DashboardHeader.vue'
import InitialsAvatar from '../components/InitialsAvatar.vue'
import checkMark from '../assets/figma/check-mark.svg'
import { useClinicStore } from '../stores/clinic'
import { formatDate, formatTime, toDateKey } from '../utils/datetime'

const route = useRoute()
const router = useRouter()
const clinic = useClinicStore()

const state = computed(() => route.meta.state) // 'confirmed' | 'cancel' | undefined (= booking)
const loading = ref(true)
const loadError = ref('')
const submitError = ref('')
const busy = ref(false)

// ---- booking ---------------------------------------------------------------------
const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
const today = new Date()
const displayedMonth = ref(new Date(today.getFullYear(), today.getMonth(), 1))
const doctorId = ref(null)
const patientId = ref(null)
const selectedPatient = ref(null)
const patientQuery = ref('')
const patientResults = ref([])
const selectedDate = ref('')
const selectedTime = ref('')
let searchTimer

const doctor = computed(() => clinic.doctors.find((item) => item.id === doctorId.value))
const patientOptions = computed(() => {
  const found = patientResults.value
  const chosen = selectedPatient.value
  return chosen && !found.some((item) => item.id === chosen.id) ? [chosen, ...found] : found
})

const monthLabel = computed(() =>
  new Intl.DateTimeFormat('en', { month: 'long', year: 'numeric' }).format(displayedMonth.value),
)

const calendarDays = computed(() => {
  const year = displayedMonth.value.getFullYear()
  const month = displayedMonth.value.getMonth()
  const firstWeekday = new Date(year, month, 1).getDay()
  const numberOfDays = new Date(year, month + 1, 0).getDate()
  const days = Array.from({ length: firstWeekday }, (_, index) => ({
    key: `blank-${index}`,
    dateKey: '',
  }))
  for (let dayNumber = 1; dayNumber <= numberOfDays; dayNumber += 1) {
    const dateKey = toDateKey(new Date(year, month, dayNumber))
    days.push({
      key: dateKey,
      dateKey,
      dayNumber,
      isPast: dateKey < toDateKey(today),
      isAvailable: clinic.availableTimes(doctorId.value, dateKey).length > 0,
    })
  }
  return days
})

const availableTimes = computed(() => clinic.availableTimes(doctorId.value, selectedDate.value))
const selectionMessage = computed(() => {
  if (!clinic.doctors.length && !loading.value) return 'There are no doctors to book yet.'
  if (!patientId.value) return 'Choose the patient to continue.'
  if (!selectedDate.value) return 'Choose an available date to continue.'
  if (!selectedTime.value) return 'Choose an available time to continue.'
  return ''
})

watch(availableTimes, (times) => {
  if (selectedTime.value && !times.includes(selectedTime.value)) selectedTime.value = ''
})
watch(doctorId, () => {
  selectedTime.value = ''
})
watch(patientQuery, (query) => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => searchPatients(query), 250)
})
onBeforeUnmount(() => window.clearTimeout(searchTimer))

async function searchPatients(query) {
  try {
    patientResults.value = await clinic.searchPatients(query)
  } catch (failure) {
    submitError.value = failure.message
  }
}

watch(patientId, (id) => {
  selectedPatient.value = patientOptions.value.find((item) => item.id === id) ?? null
})

function changeMonth(offset) {
  const year = displayedMonth.value.getFullYear()
  const month = displayedMonth.value.getMonth()
  displayedMonth.value = new Date(year, month + offset, 1)
}

function selectDate(dateKey) {
  if (dateKey !== selectedDate.value) selectedTime.value = ''
  selectedDate.value = dateKey
}

async function confirmBooking() {
  if (selectionMessage.value) return
  submitError.value = ''
  busy.value = true
  try {
    await clinic.bookAppointment({
      patientId: patientId.value,
      doctorId: doctorId.value,
      dateKey: selectedDate.value,
      time: selectedTime.value,
      patientName: selectedPatient.value?.full_name ?? '',
      doctorName: doctor.value?.username ?? '',
    })
    router.push('/appointments/confirmed')
  } catch (failure) {
    // e.g. 409 "The doctor is already booked at that time." - refresh so the slot disappears.
    submitError.value = failure.message
    selectedTime.value = ''
    await clinic.loadAppointments().catch(() => {})
  } finally {
    busy.value = false
  }
}

// ---- confirmation ----------------------------------------------------------------
const booking = computed(() => clinic.lastBooking)

// ---- cancellation ----------------------------------------------------------------
const target = computed(() =>
  clinic.appointments.find((item) => item.id === Number(route.query.id)),
)
const cancellable = computed(() => target.value?.status === 'Scheduled')

async function cancelBooking() {
  submitError.value = ''
  busy.value = true
  try {
    await clinic.cancelAppointment(target.value.id)
    clinic.notify('Appointment cancelled. The time slot is free again.')
    router.push('/reception')
  } catch (failure) {
    submitError.value = failure.message
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    if (state.value === 'confirmed') {
      if (!booking.value) router.replace('/reception') // e.g. the page was reloaded
      return
    }
    if (state.value === 'cancel') {
      await clinic.loadAppointments()
      return
    }
    await Promise.all([clinic.loadDoctors(), clinic.loadSlots(), clinic.loadAppointments()])
    const wanted = Number(route.query.doctor)
    doctorId.value = clinic.doctors.some((item) => item.id === wanted)
      ? wanted
      : (clinic.doctors[0]?.id ?? null)
    await searchPatients('')
    const wantedPatient = Number(route.query.patient)
    if (wantedPatient) {
      selectedPatient.value = await clinic.getPatient(wantedPatient).catch(() => null)
      if (selectedPatient.value) patientId.value = wantedPatient
    }
  } catch (failure) {
    loadError.value = failure.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main v-if="state === 'confirmed' && booking" class="confirmation-page">
    <BrandMark compact />
    <section class="confirmation-card">
      <div class="check-circle"><img :src="checkMark" alt="Appointment confirmed" /></div>
      <h1>Appointment booked</h1>
      <div class="confirmation-doctor">
        <InitialsAvatar :name="booking.doctorName" :size="70" />
        <div>
          <strong>{{ booking.doctorName }}</strong
          ><span>for {{ booking.patientName }}</span>
        </div>
      </div>
      <div class="confirmation-pills">
        <span>{{ formatDate(booking.dateKey) }}</span
        ><span>{{ formatTime(booking.time) }}</span>
      </div>
      <p>You can view or cancel this appointment from the upcoming appointments list.</p>
      <RouterLink class="button button-primary" to="/reception">Back to dashboard</RouterLink>
    </section>
  </main>

  <main v-else-if="state === 'cancel'" class="dashboard-page">
    <DashboardHeader />
    <section class="cancel-card">
      <template v-if="loading">
        <p class="empty-state">Loading…</p>
      </template>
      <template v-else-if="target && cancellable">
        <h1>Cancel this appointment?</h1>
        <InitialsAvatar :name="target.doctorName" :size="92" />
        <h2>{{ target.doctorName }}</h2>
        <p class="subtle-text">Patient: {{ target.patientName }}</p>
        <div class="confirmation-pills">
          <span>{{ formatDate(target.dateKey) }}</span
          ><span>{{ formatTime(target.time) }}</span>
        </div>
        <p class="subtle-text">Cancelling will free this time slot for other patients.</p>
        <p v-if="submitError" class="form-error" role="alert">{{ submitError }}</p>
        <div class="cancel-actions">
          <RouterLink class="button button-muted" to="/reception">Keep appointment</RouterLink>
          <button
            class="button button-muted danger-button"
            type="button"
            :disabled="busy"
            @click="cancelBooking"
          >
            {{ busy ? 'Cancelling…' : 'Yes, cancel' }}
          </button>
        </div>
      </template>
      <template v-else>
        <h1>Nothing to cancel</h1>
        <p class="subtle-text">
          {{
            loadError ||
            (target
              ? `This appointment is already ${target.status.toLowerCase()}.`
              : 'We could not find that appointment.')
          }}
        </p>
        <RouterLink class="button button-muted" to="/reception">Back to dashboard</RouterLink>
      </template>
    </section>
  </main>

  <main v-else-if="!state" class="booking-page">
    <header class="booking-brand"><BrandMark compact /></header>
    <RouterLink class="button button-muted booking-back" to="/reception">Back</RouterLink>
    <h1>Book an appointment</h1>
    <p v-if="loadError" class="form-error" role="alert">{{ loadError }}</p>
    <section class="booking-content">
      <aside class="booking-doctor">
        <InitialsAvatar v-if="doctor" :name="doctor.username" :size="132" square />
        <h2>{{ doctor?.username || 'No doctor' }}</h2>
        <label v-if="clinic.doctors.length > 1" class="booking-doctor-picker">
          Doctor
          <select v-model.number="doctorId">
            <option v-for="item in clinic.doctors" :key="item.id" :value="item.id">
              {{ item.username }}
            </option>
          </select>
        </label>
      </aside>
      <section class="calendar-panel">
        <div class="calendar-controls">
          <button type="button" aria-label="Previous month" @click="changeMonth(-1)">‹</button>
          <strong>{{ monthLabel }}</strong>
          <button type="button" aria-label="Next month" @click="changeMonth(1)">›</button>
        </div>
        <div class="calendar-grid">
          <span v-for="day in weekDays" :key="day">{{ day }}</span>
          <template v-for="day in calendarDays" :key="day.key">
            <span v-if="!day.dateKey" class="calendar-empty" aria-hidden="true"></span>
            <button
              v-else
              type="button"
              :disabled="!day.isAvailable"
              :class="{
                selected: selectedDate === day.dateKey,
                unavailable: !day.isAvailable,
                past: day.isPast,
              }"
              :aria-label="`${formatDate(day.dateKey)}${day.isAvailable ? ', available' : ', unavailable'}`"
              :aria-pressed="selectedDate === day.dateKey"
              @click="selectDate(day.dateKey)"
            >
              {{ day.dayNumber }}
            </button>
          </template>
        </div>
      </section>
      <section class="time-picker">
        <h2>{{ selectedDate ? 'Available times' : 'Select a date first' }}</h2>
        <button
          v-for="time in availableTimes"
          :key="time"
          type="button"
          :class="{ selected: selectedTime === time }"
          @click="selectedTime = time"
        >
          {{ formatTime(time) }}
        </button>
        <p v-if="selectedDate && !availableTimes.length" class="empty-state">
          No time slots are free on this date.
        </p>
      </section>
    </section>
    <section class="booking-patient">
      <label>
        Find a patient
        <input
          v-model="patientQuery"
          type="search"
          placeholder="Name, phone number or patient ID"
          autocomplete="off"
        />
      </label>
      <label>
        Patient
        <select v-model.number="patientId">
          <option :value="null" disabled>
            {{ patientOptions.length ? 'Select a patient' : 'No patients found' }}
          </option>
          <option v-for="patient in patientOptions" :key="patient.id" :value="patient.id">
            {{ patient.full_name }} · born {{ formatDate(patient.date_of_birth) }}
          </option>
        </select>
      </label>
      <RouterLink class="text-link" to="/reception/patients/new">Register a new patient</RouterLink>
    </section>
    <div class="booking-summary">
      <span>{{ selectedDate ? formatDate(selectedDate) : 'Select date' }}</span>
      <span>{{ selectedTime ? formatTime(selectedTime) : 'Select time' }}</span>
    </div>
    <p v-if="submitError" class="form-error" role="alert">{{ submitError }}</p>
    <p v-else-if="selectionMessage" class="booking-validation" role="status">
      {{ selectionMessage }}
    </p>
    <button
      class="button button-primary booking-confirm"
      type="button"
      :disabled="busy || !!selectionMessage"
      @click="confirmBooking"
    >
      {{ busy ? 'Booking…' : 'Confirm appointment' }}
    </button>
  </main>
</template>
