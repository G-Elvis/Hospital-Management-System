<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardHeader from '../components/DashboardHeader.vue'
import BrandMark from '../components/BrandMark.vue'
import { useCareSyncStore } from '../stores/careSync'
import checkMark from '../assets/figma/check-mark.svg'

const route = useRoute()
const router = useRouter()
const store = useCareSyncStore()
const state = computed(() => route.meta.state)
const doctor = computed(() => store.selectedDoctor)
const appointment = computed(() => store.selectedAppointment)
const weekDays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
const today = new Date()
const storedDate = store.selectedDate ? new Date(`${store.selectedDate}T00:00:00`) : today
const displayedMonth = ref(new Date(storedDate.getFullYear(), storedDate.getMonth(), 1))
const cancellationReason = ref('')

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
    dayNumber: '',
    isPast: false,
    isAvailable: false,
  }))

  for (let dayNumber = 1; dayNumber <= numberOfDays; dayNumber += 1) {
    const date = new Date(year, month, dayNumber)
    const dateKey = toDateKey(date)
    const isPast = dateKey < toDateKey(today)
    const isAvailable = !isPast && store.getAvailableTimes(dateKey).length > 0

    days.push({
      key: dateKey,
      dateKey,
      dayNumber,
      isPast,
      isAvailable,
    })
  }

  return days
})

const availableTimes = computed(() =>
  store.selectedDate ? store.getAvailableTimes(store.selectedDate) : [],
)

const selectedDateLabel = computed(() =>
  store.selectedDate ? formatDate(store.selectedDate) : 'Select date',
)

const selectionMessage = computed(() => {
  if (!store.selectedDate) return 'Choose an available date to continue.'
  if (!store.selectedTime) return 'Choose an available time to continue.'
  return ''
})

watch(
  () => route.query.doctor,
  (id) => {
    if (id && store.doctors.some((person) => person.id === id)) {
      store.selectedDoctorId = id
    }
  },
  { immediate: true },
)

watch(availableTimes, (times) => {
  if (store.selectedTime && !times.includes(store.selectedTime)) {
    store.chooseBooking(store.selectedDoctorId, store.selectedDate, '')
  }
})

onMounted(() => {
  if (!store.selectedDoctorId) store.selectedDoctorId = 'grace-miller'
})

function chooseTime(time) {
  store.chooseBooking(store.selectedDoctorId, store.selectedDate, time)
}

function toDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatDate(dateKey) {
  return new Intl.DateTimeFormat('en', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(`${dateKey}T00:00:00`))
}

function changeMonth(offset) {
  const year = displayedMonth.value.getFullYear()
  const month = displayedMonth.value.getMonth()
  displayedMonth.value = new Date(year, month + offset, 1)
}

function selectDate(dateKey) {
  const selectedTime = dateKey === store.selectedDate ? store.selectedTime : ''
  store.chooseBooking(store.selectedDoctorId, dateKey, selectedTime)
}

function confirmBooking() {
  if (!store.selectedDate || !store.selectedTime) {
    store.notify('Choose an available date and time before confirming.')
    return
  }

  const appointment = store.confirmBooking()
  if (!appointment) {
    store.notify('Choose an available date and time before confirming.')
    return
  }
  router.push('/appointments/confirmed')
}

function cancelBooking() {
  if (!cancellationReason.value.trim()) {
    store.notify('Enter a cancellation reason before continuing.')
    return
  }
  if (store.cancelAppointment(appointment.value?.id, cancellationReason.value)) {
    router.push('/patient')
  }
}
</script>

<template>
  <main v-if="state === 'confirmed'" class="confirmation-page">
    <BrandMark compact />
    <section class="confirmation-card">
      <div class="check-circle"><img :src="checkMark" alt="Appointment confirmed" /></div>
      <h1>Appointment booked</h1>
      <div class="confirmation-doctor">
        <img :src="doctor.photo" :alt="doctor.name" />
        <div>
          <strong>{{ doctor.name }}</strong
          ><span>{{ doctor.specialty }}</span>
        </div>
      </div>
      <div class="confirmation-pills">
        <span>{{ appointment?.date || selectedDateLabel }}</span
        ><span>{{ appointment?.time || store.selectedTime }}</span>
      </div>
      <p>You can view or cancel this appointment from My appointments on your dashboard.</p>
      <RouterLink class="button button-primary" to="/patient">My dashboard</RouterLink>
    </section>
  </main>

  <main v-else-if="state === 'cancel'" class="dashboard-page">
    <DashboardHeader />
    <section class="cancel-card">
      <h1>Cancel this appointment?</h1>
      <img :src="doctor.photo" :alt="doctor.name" />
      <h2>{{ doctor.name }}</h2>
      <p class="subtle-text">{{ doctor.specialty }}</p>
      <div class="confirmation-pills">
        <span>{{ appointment?.date }}</span
        ><span>{{ appointment?.time }}</span>
      </div>
      <p class="subtle-text">Cancelling will free this time slot for other patients.</p>
      <label class="cancel-reason">
        Cancellation reason
        <textarea
          v-model="cancellationReason"
          rows="3"
          maxlength="240"
          placeholder="Let the patient know why this appointment is being cancelled."
          required
        ></textarea>
      </label>
      <div class="cancel-actions">
        <RouterLink class="button button-muted" to="/patient">Keep appointment</RouterLink>
        <button
          class="button button-muted danger-button"
          type="button"
          :disabled="!cancellationReason.trim()"
          @click="cancelBooking"
        >
          Yes, cancel
        </button>
      </div>
    </section>
  </main>

  <main v-else class="booking-page">
    <header class="booking-brand"><BrandMark compact /></header>
    <RouterLink class="button button-muted booking-back" to="/patient"
      >Back</RouterLink
    >
    <h1>Book your appointment</h1>
    <section class="booking-content">
      <aside class="booking-doctor">
        <img :src="doctor.photo" :alt="doctor.name" />
        <h2>{{ doctor.name }}</h2>
        <p>{{ doctor.specialty }}</p>
        <blockquote>
          Thank you for selecting me!<br />Ready to deliver the best treatment
        </blockquote>
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
                selected: store.selectedDate === day.dateKey,
                unavailable: !day.isAvailable,
                past: day.isPast,
              }"
              :aria-label="`${formatDate(day.dateKey)}${day.isAvailable ? ', available' : ', unavailable'}`"
              :aria-pressed="store.selectedDate === day.dateKey"
              @click="selectDate(day.dateKey)"
            >
              {{ day.dayNumber }}
            </button>
          </template>
        </div>
      </section>
      <section class="time-picker">
        <h2>{{ store.selectedDate ? 'Available times' : 'Select a date first' }}</h2>
        <button
          v-for="time in availableTimes"
          :key="time"
          type="button"
          :class="{ selected: store.selectedTime === time }"
          @click="chooseTime(time)"
        >
          {{ time }}
        </button>
        <p v-if="store.selectedDate && !availableTimes.length" class="empty-state">
          No sample time slots are available on this date.
        </p>
      </section>
    </section>
    <div class="booking-summary">
      <span>{{ selectedDateLabel }}</span>
      <span>{{ store.selectedTime || 'Select time' }}</span>
    </div>
    <p v-if="selectionMessage" class="booking-validation" role="status">{{ selectionMessage }}</p>
    <button
      class="button button-primary booking-confirm"
      type="button"
      :disabled="!store.selectedDate || !store.selectedTime"
      @click="confirmBooking"
    >
      Confirm appointment
    </button>
  </main>
</template>
