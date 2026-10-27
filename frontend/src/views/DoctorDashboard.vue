<script setup>
import { computed, reactive, ref, watch } from 'vue'
import DashboardHeader from '../components/DashboardHeader.vue'
import { useCareSyncStore } from '../stores/careSync'

const store = useCareSyncStore()
const activeSection = ref('appointments')
const activeFilter = ref('All')
const filterDate = ref('')
const selectedCalendarDate = ref('')
const displayedMonth = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const editingAvailabilityId = ref('')
const blockedDate = ref('')
const blockedReason = ref('')
const reschedulingAppointment = ref(null)
const rescheduleDate = ref('')
const rescheduleTime = ref('')
const availabilityForm = reactive({
  days: [],
  startTime: '09:00',
  endTime: '17:00',
  duration: 30,
  breakStart: '12:00',
  breakEnd: '13:00',
})

const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const statusFilters = ['All', 'Pending', 'Confirmed', 'Completed', 'Cancelled', 'Declined']
const doctorAvailability = computed(() =>
  store.consultationAvailability.filter(
    (availability) => (availability.doctorId ?? 'grace-miller') === store.selectedDoctorId,
  ),
)
const monthLabel = computed(() =>
  new Intl.DateTimeFormat('en', { month: 'long', year: 'numeric' }).format(displayedMonth.value),
)

const appointments = computed(() =>
  store.appointments
    .filter((appointment) => appointment.doctorId === store.selectedDoctorId)
    .filter((appointment) => activeFilter.value === 'All' || appointment.status === activeFilter.value)
    .filter((appointment) => !filterDate.value || appointment.dateKey === filterDate.value)
    .sort((first, second) =>
      `${first.dateKey ?? ''} ${first.time}`.localeCompare(`${second.dateKey ?? ''} ${second.time}`),
    ),
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
  }))

  for (let dayNumber = 1; dayNumber <= numberOfDays; dayNumber += 1) {
    const date = new Date(year, month, dayNumber)
    const key = toDateKey(date)
    const appointmentsForDate = store.appointments.filter(
      (appointment) =>
        appointment.doctorId === store.selectedDoctorId &&
        appointment.dateKey === key &&
        ['Pending', 'Confirmed'].includes(appointment.status),
    )
    const hasSchedule = doctorAvailability.value.some(
      (availability) =>
        availability.day === new Intl.DateTimeFormat('en', { weekday: 'long' }).format(date),
    )
    const isBlocked = store.unavailableDates.some(
      (unavailable) => unavailable.date === key && unavailable.doctorId === store.selectedDoctorId,
    )
    const isPast = key < toDateKey(new Date())
    const availableCount = store.getAvailableTimes(key).length
    const status = isPast || isBlocked || !hasSchedule
      ? 'unavailable'
      : availableCount === 0
        ? 'full'
        : 'available'
    days.push({
      key,
      dateKey: key,
      dayNumber,
      appointments: appointmentsForDate,
      status,
    })
  }
  return days
})

const selectedDateAppointments = computed(() =>
  store.appointments.filter(
    (appointment) =>
      appointment.doctorId === store.selectedDoctorId &&
      appointment.dateKey === selectedCalendarDate.value,
  ),
)

const rescheduleTimes = computed(() =>
  rescheduleDate.value && reschedulingAppointment.value
    ? store.getAvailableTimes(
        rescheduleDate.value,
        reschedulingAppointment.value.doctorId,
        reschedulingAppointment.value.id,
      )
    : [],
)

watch(rescheduleTimes, (times) => {
  if (rescheduleTime.value && !times.includes(rescheduleTime.value)) {
    rescheduleTime.value = ''
  }
})

function toDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatDate(dateKey) {
  if (!dateKey) return 'Select a date'
  return new Intl.DateTimeFormat('en', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(`${dateKey}T00:00:00`))
}

function changeMonth(offset) {
  displayedMonth.value = new Date(
    displayedMonth.value.getFullYear(),
    displayedMonth.value.getMonth() + offset,
    1,
  )
}

function selectCalendarDate(dateKey) {
  selectedCalendarDate.value = dateKey
}

function clearAvailabilityForm() {
  availabilityForm.days = []
  availabilityForm.startTime = '09:00'
  availabilityForm.endTime = '17:00'
  availabilityForm.duration = 30
  availabilityForm.breakStart = '12:00'
  availabilityForm.breakEnd = '13:00'
  editingAvailabilityId.value = ''
}

function editAvailability(availability) {
  availabilityForm.days = [availability.day]
  availabilityForm.startTime = availability.startTime
  availabilityForm.endTime = availability.endTime
  availabilityForm.duration = Number(availability.duration || 30)
  availabilityForm.breakStart = availability.breakStart || ''
  availabilityForm.breakEnd = availability.breakEnd || ''
  editingAvailabilityId.value = availability.id
}

function saveAvailability() {
  if (!availabilityForm.days.length) {
    store.notify('Select at least one working day.')
    return
  }

  for (const day of availabilityForm.days) {
    const existing = doctorAvailability.value.find((item) => item.day === day)
    const saved = store.saveAvailability({
      day,
      startTime: availabilityForm.startTime,
      endTime: availabilityForm.endTime,
      duration: availabilityForm.duration,
      breakStart: availabilityForm.breakStart,
      breakEnd: availabilityForm.breakEnd,
      id: existing?.id ?? (day === availabilityForm.days[0] ? editingAvailabilityId.value : ''),
    })
    if (!saved) return
  }
  clearAvailabilityForm()
  store.notify('Availability saved. Patient booking slots are updated.')
}

function removeAvailability(availabilityId) {
  store.removeAvailability(availabilityId)
  if (editingAvailabilityId.value === availabilityId) clearAvailabilityForm()
}

function blockSelectedDate() {
  if (store.blockDate(blockedDate.value, blockedReason.value)) {
    blockedDate.value = ''
    blockedReason.value = ''
    store.notify('Date marked unavailable to patients.')
  }
}

function appointmentPatient(appointment) {
  return store.messages.find((message) => message.contact === appointment.patient)
}

function confirmStatusChange(appointment, status) {
  const action = status === 'Confirmed' ? 'accept' : 'decline'
  if (!window.confirm(`${action === 'accept' ? 'Accept' : 'Decline'} ${appointment.patient}'s appointment request?`)) {
    return
  }
  store.updateAppointmentStatus(appointment.id, status)
  store.notify(`Appointment ${status.toLowerCase()}.`)
}

function completeAppointment(appointment) {
  if (!window.confirm(`Mark ${appointment.patient}'s appointment as completed?`)) return
  store.updateAppointmentStatus(appointment.id, 'Completed')
}

function cancelAppointment(appointment) {
  const reason = window.prompt('Enter a cancellation reason for the patient:')
  if (reason === null) return
  if (!reason.trim()) {
    store.notify('Enter a cancellation reason before cancelling.')
    return
  }
  if (window.confirm(`Cancel ${appointment.patient}'s appointment?`)) {
    store.cancelAppointment(appointment.id, reason)
    store.notify('Appointment cancelled and its time slot released.')
  }
}

function openReschedule(appointment) {
  reschedulingAppointment.value = appointment
  rescheduleDate.value = appointment.dateKey
  rescheduleTime.value = ''
}

function saveReschedule() {
  if (!rescheduleTime.value) {
    store.notify('Choose an available time before rescheduling.')
    return
  }
  if (
    !window.confirm(
      `Reschedule ${reschedulingAppointment.value.patient}'s appointment to ${formatDate(rescheduleDate.value)} at ${rescheduleTime.value}?`,
    )
  ) {
    return
  }
  if (
    store.rescheduleAppointment(
      reschedulingAppointment.value.id,
      rescheduleDate.value,
      rescheduleTime.value,
    )
  ) {
    reschedulingAppointment.value = null
    store.notify('Appointment rescheduled.')
  }
}
</script>

<template>
  <main class="dashboard-page">
    <DashboardHeader role="doctor" show-back />
    <h1 class="page-section-title">Doctor dashboard</h1>
    <nav class="doctor-section-tabs" aria-label="Doctor dashboard sections">
      <button
        type="button"
        :class="{ active: activeSection === 'appointments' }"
        @click="activeSection = 'appointments'"
      >
        Appointment Management
      </button>
      <button
        type="button"
        :class="{ active: activeSection === 'availability' }"
        @click="activeSection = 'availability'"
      >
        Availability Management
      </button>
    </nav>

    <section v-if="activeSection === 'appointments'" class="doctor-management">
      <div class="management-heading">
        <div>
          <h2>Appointment Management</h2>
          <p>Review patient requests and manage your appointment history.</p>
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

      <div class="doctor-management-grid">
        <div class="doctor-appointment-list">
          <article
            v-for="appointment in appointments"
            :key="appointment.id"
            class="doctor-appointment-card"
          >
            <div class="doctor-appointment-patient">
              <img
                v-if="appointmentPatient(appointment)?.photo"
                :src="appointmentPatient(appointment).photo"
                :alt="appointment.patient"
              />
              <span v-else class="patient-initial">{{ appointment.patient?.charAt(0) || 'P' }}</span>
              <div>
                <h3>{{ appointment.patient }}</h3>
                <p>{{ appointment.visit || 'Consultation' }}</p>
                <p v-if="appointment.patientEmail">{{ appointment.patientEmail }}</p>
                <p v-if="appointment.patientPhone">{{ appointment.patientPhone }}</p>
              </div>
            </div>
            <div class="doctor-appointment-info">
              <strong>{{ appointment.date || formatDate(appointment.dateKey) }}</strong>
              <span>{{ appointment.time }} · {{ appointment.duration || 30 }} minutes</span>
              <span v-if="appointment.notes">{{ appointment.notes }}</span>
              <span class="appointment-status" :class="`status-${appointment.status.toLowerCase()}`">
                {{ appointment.status }}
              </span>
              <span v-if="appointment.cancellationReason" class="cancellation-reason">
                Reason: {{ appointment.cancellationReason }}
              </span>
            </div>
            <div v-if="['Pending', 'Confirmed'].includes(appointment.status)" class="appointment-actions">
              <template v-if="appointment.status === 'Pending'">
                <button class="button button-primary" type="button" @click="confirmStatusChange(appointment, 'Confirmed')">
                  Accept
                </button>
                <button class="button button-muted danger-button" type="button" @click="confirmStatusChange(appointment, 'Declined')">
                  Decline
                </button>
              </template>
              <template v-else>
                <button class="button button-muted" type="button" @click="openReschedule(appointment)">
                  Reschedule
                </button>
                <button class="button button-muted danger-button" type="button" @click="cancelAppointment(appointment)">
                  Cancel
                </button>
                <button class="button button-primary" type="button" @click="completeAppointment(appointment)">
                  Complete
                </button>
              </template>
            </div>
          </article>
          <p v-if="!appointments.length" class="empty-state">No appointments match these filters.</p>
        </div>

        <aside class="doctor-dash-side">
          <section>
            <h2>Medical history</h2>
            <RouterLink
              class="button button-muted wide-button"
              :to="{ name: 'patient-history', params: { id: 1 }, query: { tab: 'Medical report' } }"
              >Medical report</RouterLink
            >
            <RouterLink
              class="button button-muted wide-button"
              :to="{ name: 'patient-history', params: { id: 1 }, query: { tab: 'Test Results' } }"
              >Test Results</RouterLink
            >
            <RouterLink
              class="button button-muted wide-button"
              :to="{ name: 'patient-history', params: { id: 1 }, query: { tab: 'Prescriptions' } }"
              >Prescriptions</RouterLink
            >
          </section>
          <section class="unread-chats">
            <h2>View unread chats</h2>
            <RouterLink class="message-preview" to="/doctor/chat"
              >Message from John <span>10:00pm</span></RouterLink
            >
          </section>
        </aside>
      </div>
    </section>

    <section v-else class="availability-section doctor-availability">
      <div class="availability-heading">
        <div>
          <h2>Availability Management</h2>
          <p>Manage your working hours, consultation breaks, leave, and patient booking slots.</p>
        </div>
      </div>
      <div class="availability-layout">
        <div class="availability-calendar">
          <div class="calendar-controls">
            <button type="button" aria-label="Previous month" @click="changeMonth(-1)">‹</button>
            <strong>{{ monthLabel }}</strong>
            <button type="button" aria-label="Next month" @click="changeMonth(1)">›</button>
          </div>
          <div class="calendar-grid availability-calendar-grid">
            <span v-for="day in ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']" :key="day">
              {{ day }}
            </span>
            <template v-for="day in calendarDays" :key="day.key">
              <span v-if="!day.dateKey" class="calendar-empty" aria-hidden="true"></span>
              <button
                v-else
                type="button"
                :class="[
                  `day-${day.status}`,
                  { selected: selectedCalendarDate === day.dateKey },
                ]"
                :aria-label="`${formatDate(day.dateKey)}: ${day.status}${day.appointments?.length ? `, ${day.appointments.length} appointments` : ''}`"
                @click="selectCalendarDate(day.dateKey)"
              >
                {{ day.dayNumber }}
                <small v-if="day.appointments?.length">{{ day.appointments.length }}</small>
              </button>
            </template>
          </div>
          <div class="calendar-legend">
            <span><i class="legend-available"></i> Available</span>
            <span><i class="legend-full"></i> Fully booked</span>
            <span><i class="legend-unavailable"></i> Unavailable</span>
          </div>
          <div v-if="selectedCalendarDate" class="calendar-date-details">
            <h3>{{ formatDate(selectedCalendarDate) }}</h3>
            <p v-if="!selectedDateAppointments.length">No appointments scheduled.</p>
            <p v-for="appointment in selectedDateAppointments" :key="appointment.id">
              {{ appointment.time }} · {{ appointment.patient }} — {{ appointment.status }}
            </p>
          </div>
        </div>

        <div class="availability-controls">
          <h3>Working days and hours</h3>
          <ul v-if="doctorAvailability.length" class="availability-list">
            <li
              v-for="availability in doctorAvailability"
              :key="availability.id"
              class="availability-row"
            >
              <strong>{{ availability.day }}</strong>
              <span>
                {{ availability.startTime }}–{{ availability.endTime }} ·
                {{ availability.duration || 30 }} min
                <template v-if="availability.breakStart && availability.breakEnd">
                  · Break {{ availability.breakStart }}–{{ availability.breakEnd }}
                </template>
              </span>
              <button class="button button-muted" type="button" @click="editAvailability(availability)">
                Edit
              </button>
              <button
                class="button button-muted danger-button"
                type="button"
                @click="removeAvailability(availability.id)"
              >
                Remove
              </button>
            </li>
          </ul>
          <p v-else class="empty-state">No working hours configured. Add your working days below.</p>

          <form class="availability-form availability-editor" @submit.prevent="saveAvailability">
            <fieldset class="working-day-options">
              <legend>Working days</legend>
              <label v-for="day in weekDays" :key="day">
                <input v-model="availabilityForm.days" type="checkbox" :value="day" />
                {{ day }}
              </label>
            </fieldset>
            <label>
              Start time
              <input v-model="availabilityForm.startTime" type="time" required />
            </label>
            <label>
              End time
              <input v-model="availabilityForm.endTime" type="time" required />
            </label>
            <label>
              Appointment duration
              <select v-model.number="availabilityForm.duration">
                <option :value="15">15 minutes</option>
                <option :value="30">30 minutes</option>
                <option :value="60">60 minutes</option>
              </select>
            </label>
            <label>
              Break starts
              <input v-model="availabilityForm.breakStart" type="time" />
            </label>
            <label>
              Break ends
              <input v-model="availabilityForm.breakEnd" type="time" />
            </label>
            <button class="button button-primary" type="submit">
              {{ editingAvailabilityId ? 'Save hours' : 'Add availability' }}
            </button>
            <button
              v-if="editingAvailabilityId"
              class="button button-muted"
              type="button"
              @click="clearAvailabilityForm"
            >
              Stop editing
            </button>
          </form>

          <form class="block-date-form" @submit.prevent="blockSelectedDate">
            <h3>Block a date</h3>
            <label>
              Date
              <input v-model="blockedDate" type="date" :min="toDateKey(new Date())" required />
            </label>
            <label>
              Reason
              <input v-model="blockedReason" type="text" maxlength="120" placeholder="Leave, commitment..." />
            </label>
            <button class="button button-muted" type="submit">Mark unavailable</button>
          </form>
          <ul v-if="store.unavailableDates.length" class="blocked-date-list">
            <li
              v-for="item in store.unavailableDates.filter((date) => date.doctorId === store.selectedDoctorId)"
              :key="item.date"
            >
              <span>{{ formatDate(item.date) }}<small v-if="item.reason"> · {{ item.reason }}</small></span>
              <button class="button button-muted" type="button" @click="store.unblockDate(item.date)">
                Restore
              </button>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <div v-if="reschedulingAppointment" class="dialog-backdrop" @click.self="reschedulingAppointment = null">
      <section class="reschedule-dialog" role="dialog" aria-modal="true" aria-labelledby="reschedule-title">
        <h2 id="reschedule-title">Reschedule appointment</h2>
        <p>{{ reschedulingAppointment.patient }} · {{ reschedulingAppointment.date }}</p>
        <label>
          New date
          <input v-model="rescheduleDate" type="date" :min="toDateKey(new Date())" />
        </label>
        <label>
          Available time
          <select v-model="rescheduleTime" :disabled="!rescheduleTimes.length">
            <option value="" disabled>Choose an available time</option>
            <option v-for="time in rescheduleTimes" :key="time" :value="time">{{ time }}</option>
          </select>
        </label>
        <p v-if="rescheduleDate && !rescheduleTimes.length" class="empty-state">
          No available times on this date.
        </p>
        <div class="dialog-actions">
          <button class="button button-muted" type="button" @click="reschedulingAppointment = null">
            Keep current time
          </button>
          <button class="button button-primary" type="button" @click="saveReschedule">
            Save reschedule
          </button>
        </div>
      </section>
    </div>
    <div v-if="store.lastNotice" class="toast" role="status">{{ store.lastNotice }}</div>
  </main>
</template>
