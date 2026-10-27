import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'

import gracePhoto from '../assets/figma/doctor-grace.png'
import jakePhoto from '../assets/figma/doctor-jake.png'
import lauraPhoto from '../assets/figma/doctor-laura.png'
import kenPhoto from '../assets/figma/patient-ken.png'

const STORAGE_KEY = 'caresync-demo-data-v1'
const ACTIVE_STATUSES = ['Pending', 'Confirmed']

function dateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatDate(date) {
  return new Intl.DateTimeFormat('en', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

function formatTime(minutes) {
  const hour = Math.floor(minutes / 60)
  const minute = minutes % 60
  return `${hour % 12 || 12}:${String(minute).padStart(2, '0')}${hour < 12 ? 'am' : 'pm'}`
}

function timeToMinutes(time) {
  if (!time) return null
  const match = time.match(/^(\d{1,2}):(\d{2})(am|pm)$/i)
  if (match) {
    const hour = Number(match[1]) % 12
    return hour * 60 + Number(match[2]) + (match[3].toLowerCase() === 'pm' ? 720 : 0)
  }
  const [hour, minute] = time.split(':').map(Number)
  return hour * 60 + minute
}

function getStoredData() {
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY)
    if (!saved) return null
    return JSON.parse(saved)
  } catch (error) {
    console.warn('CareSync demo data could not be loaded from localStorage.', error)
    return null
  }
}

function makeDefaultAppointments() {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  while (tomorrow.getDay() === 0 || tomorrow.getDay() === 6) tomorrow.setDate(tomorrow.getDate() + 1)
  const nextDay = new Date()
  nextDay.setTime(tomorrow.getTime())
  nextDay.setDate(nextDay.getDate() + 1)
  while (nextDay.getDay() === 0 || nextDay.getDay() === 6) nextDay.setDate(nextDay.getDate() + 1)

  return [
    {
      id: 'appointment-1',
      doctorId: 'grace-miller',
      patient: 'Laura Aguirre',
      patientEmail: 'laura@example.com',
      patientPhone: '+1 555 010 2040',
      date: formatDate(tomorrow),
      dateKey: dateKey(tomorrow),
      time: '9:00am',
      duration: 30,
      visit: 'Initial visit',
      notes: 'Cardiology consultation',
      status: 'Pending',
    },
    {
      id: 'appointment-2',
      doctorId: 'grace-miller',
      patient: 'Ken Jackson',
      patientEmail: 'ken@example.com',
      patientPhone: '+1 555 010 2088',
      date: formatDate(nextDay),
      dateKey: dateKey(nextDay),
      time: '10:00am',
      duration: 30,
      visit: 'Follow-up',
      notes: 'Follow-up consultation',
      status: 'Confirmed',
    },
  ]
}

function makeDefaultAvailability() {
  return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map((day) => ({
    id: `availability-${day.toLowerCase()}`,
    doctorId: 'grace-miller',
    day,
    startTime: '09:00',
    endTime: '17:00',
    duration: 30,
    breakStart: '12:00',
    breakEnd: '13:00',
  }))
}

function readData() {
  const data = getStoredData()
  if (!data || typeof data !== 'object') return {}
  if (Array.isArray(data.consultationAvailability)) {
    data.consultationAvailability = data.consultationAvailability.map((availability) => ({
      ...availability,
      doctorId: availability.doctorId ?? 'grace-miller',
    }))
  }
  if (Array.isArray(data.appointments)) {
    data.appointments = data.appointments.map((appointment) => ({
      ...appointment,
      status: appointment.status === 'upcoming' ? 'Confirmed' : appointment.status,
    }))
  }
  return data
}

const storedData = readData()

export const useCareSyncStore = defineStore('careSync', () => {
  const role = ref('patient')
  const isDemoSession = ref(false)
  const doctors = ref([
    {
      id: 'grace-miller',
      name: 'Grace Miller',
      specialty: 'Cardiologist',
      photo: gracePhoto,
      description: 'A well certified cardiologist with 4 years of experience in primary care.',
    },
    {
      id: 'jake-alexandra',
      name: 'Jake Alexandra',
      specialty: 'Psychologist',
      photo: jakePhoto,
      description: 'A professional psychologist with 10 years of experience.',
    },
  ])
  const appointments = ref(storedData.appointments ?? makeDefaultAppointments())
  const consultationAvailability = ref(
    storedData.consultationAvailability ?? makeDefaultAvailability(),
  )
  const unavailableDates = ref(storedData.unavailableDates ?? [])
  const selectedAppointmentId = ref('')
  const selectedDoctorId = ref('grace-miller')
  const selectedDate = ref('')
  const selectedTime = ref('')
  const reportTab = ref('Lab results')
  const historyTab = ref('Prescriptions')
  const messages = ref([
    {
      id: 1,
      contact: 'Laura Aguirre',
      text: 'Thank you doctor.',
      time: '10:00pm',
      photo: lauraPhoto,
    },
    {
      id: 2,
      contact: 'Ken Jackson',
      text: 'See you on the 12th.',
      time: '9:15pm',
      photo: kenPhoto,
    },
  ])
  const activeChat = ref(0)
  const chatMessages = ref([
    {
      id: 1,
      from: 'patient',
      text: 'Good morning doctor, I would like to confirm my visit.',
      time: '9:58pm',
    },
    {
      id: 2,
      from: 'doctor',
      text: 'Good morning Laura. Yes, see you on the 12th at 9:00am.',
      time: '9:59pm',
    },
    { id: 3, from: 'patient', text: 'Thank you doctor.', time: '10:00pm' },
  ])
  const prescriptions = ref([
    { name: 'Amoxicillin 500mg', directions: '3 times daily for 7 days', date: 'September 9th' },
    { name: 'Ibuprofen 400mg', directions: 'As needed, after meals', date: 'September 9th' },
    { name: 'Vitamin D 1000 IU', directions: 'Once daily', date: 'August 20th' },
  ])
  const patientProfile = ref({
    name: 'USER 1',
    email: 'user@email.com',
    phone: '+000 000 000 000',
    birthDate: '',
  })
  const doctorProfile = ref({
    name: 'Dr. Grace Miller',
    specialty: 'Cardiologist',
    licence: '',
    email: 'doctor@email.com',
  })
  const lastNotice = ref('')
  let noticeTimeout
  const selectedDoctor = computed(
    () => doctors.value.find((doctor) => doctor.id === selectedDoctorId.value) ?? doctors.value[0],
  )
  const selectedAppointment = computed(
    () => appointments.value.find((appointment) => appointment.id === selectedAppointmentId.value),
  )
  const upcomingAppointments = computed(() =>
    appointments.value.filter((appointment) => ACTIVE_STATUSES.includes(appointment.status)),
  )

  watch(
    [appointments, consultationAvailability, unavailableDates],
    ([savedAppointments, savedAvailability, savedUnavailableDates]) => {
      try {
        window.localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            appointments: savedAppointments,
            consultationAvailability: savedAvailability,
            unavailableDates: savedUnavailableDates,
          }),
        )
      } catch (error) {
        console.warn('CareSync demo data could not be saved to localStorage.', error)
      }
    },
    { deep: true, immediate: true },
  )

  function signIn(nextRole = 'patient') {
    role.value = nextRole
    isDemoSession.value = true
  }

  function signOut() {
    isDemoSession.value = false
    role.value = 'patient'
  }

  function chooseBooking(doctorId, date, time) {
    selectedDoctorId.value = doctorId
    selectedDate.value = date
    selectedTime.value = time
  }

  function getAvailableTimes(date, doctorId = selectedDoctorId.value, excludeAppointmentId = '') {
    const dateObject = new Date(`${date}T00:00:00`)
    if (Number.isNaN(dateObject.getTime()) || date < dateKey(new Date())) return []
    if (unavailableDates.value.some((item) => item.date === date && item.doctorId === doctorId)) {
      return []
    }

    const day = new Intl.DateTimeFormat('en', { weekday: 'long' }).format(dateObject)
    const schedules = consultationAvailability.value.filter(
      (item) => item.day === day && (item.doctorId ?? 'grace-miller') === doctorId,
    )
    const occupied = appointments.value
      .filter(
        (appointment) =>
          appointment.doctorId === doctorId &&
          appointment.dateKey === date &&
          appointment.id !== excludeAppointmentId &&
          ACTIVE_STATUSES.includes(appointment.status),
      )
      .map((appointment) => {
        const start = timeToMinutes(appointment.time)
        return { start, end: start + Number(appointment.duration || 30) }
      })
    const available = new Set()
    const now = new Date()

    for (const schedule of schedules) {
      const start = timeToMinutes(schedule.startTime)
      const end = timeToMinutes(schedule.endTime)
      const duration = Number(schedule.duration || 30)
      const breakStart = schedule.breakStart ? timeToMinutes(schedule.breakStart) : null
      const breakEnd = schedule.breakEnd ? timeToMinutes(schedule.breakEnd) : null

      for (let slotStart = start; slotStart + duration <= end; slotStart += duration) {
        const slotEnd = slotStart + duration
        const overlapsBreak =
          breakStart !== null && breakEnd !== null && slotStart < breakEnd && slotEnd > breakStart
        const overlapsAppointment = occupied.some(
          (appointment) => slotStart < appointment.end && slotEnd > appointment.start,
        )
        const isInPast =
          date === dateKey(now) &&
          slotStart <= now.getHours() * 60 + now.getMinutes()
        if (!overlapsBreak && !overlapsAppointment && !isInPast) available.add(formatTime(slotStart))
      }
    }

    return [...available].sort((first, second) => timeToMinutes(first) - timeToMinutes(second))
  }

  function validateAppointmentSlot(date, time, doctorId, excludeAppointmentId = '') {
    if (!date || !time) return 'Choose an available date and time.'
    if (date < dateKey(new Date())) return 'Appointments cannot be scheduled in the past.'
    if (!getAvailableTimes(date, doctorId, excludeAppointmentId).includes(time)) {
      return 'That time is unavailable or conflicts with another appointment. Choose another slot.'
    }
    return ''
  }

  function confirmBooking() {
    const validationMessage = validateAppointmentSlot(
      selectedDate.value,
      selectedTime.value,
      selectedDoctorId.value,
    )
    if (validationMessage) {
      notify(validationMessage)
      return null
    }

    const appointmentDate = new Date(`${selectedDate.value}T00:00:00`)
    const appointment = {
      id: `appointment-${Date.now()}`,
      doctorId: selectedDoctorId.value,
      patient: patientProfile.value.name,
      patientEmail: patientProfile.value.email,
      patientPhone: patientProfile.value.phone,
      date: formatDate(appointmentDate),
      dateKey: selectedDate.value,
      time: selectedTime.value,
      duration:
        consultationAvailability.value.find(
          (item) =>
            (item.doctorId ?? 'grace-miller') === selectedDoctorId.value &&
            item.day === new Intl.DateTimeFormat('en', { weekday: 'long' }).format(appointmentDate),
        )?.duration ?? 30,
      visit: 'Initial visit',
      status: 'Pending',
    }
    appointments.value.unshift(appointment)
    selectedAppointmentId.value = appointment.id
    return appointment
  }

  function updateAppointmentStatus(appointmentId, status) {
    const appointment = appointments.value.find((item) => item.id === appointmentId)
    if (!appointment) {
      notify('Appointment could not be found.')
      return false
    }
    appointment.status = status
    return true
  }

  function cancelAppointment(appointmentId = selectedAppointmentId.value, reason = '') {
    const appointment = appointments.value.find((item) => item.id === appointmentId)
    if (!appointment || !ACTIVE_STATUSES.includes(appointment.status)) {
      notify('This appointment can no longer be cancelled.')
      return false
    }
    appointment.status = 'Cancelled'
    appointment.cancellationReason = reason.trim()
    return true
  }

  function rescheduleAppointment(appointmentId, date, time) {
    const appointment = appointments.value.find((item) => item.id === appointmentId)
    if (!appointment || !ACTIVE_STATUSES.includes(appointment.status)) {
      notify('This appointment can no longer be rescheduled.')
      return false
    }

    const validationMessage = validateAppointmentSlot(date, time, appointment.doctorId, appointmentId)
    if (validationMessage) {
      notify(validationMessage)
      return false
    }

    const newDate = new Date(`${date}T00:00:00`)
    appointment.dateKey = date
    appointment.date = formatDate(newDate)
    appointment.time = time
    appointment.duration =
      consultationAvailability.value.find(
        (item) =>
          (item.doctorId ?? 'grace-miller') === appointment.doctorId &&
          item.day === new Intl.DateTimeFormat('en', { weekday: 'long' }).format(newDate),
      )?.duration ?? appointment.duration ?? 30
    appointment.status = 'Confirmed'
    return true
  }

  function saveAvailability(availability) {
    const start = timeToMinutes(availability.startTime)
    const end = timeToMinutes(availability.endTime)
    const breakStart = availability.breakStart ? timeToMinutes(availability.breakStart) : null
    const breakEnd = availability.breakEnd ? timeToMinutes(availability.breakEnd) : null
    const duration = Number(availability.duration)

    if (!availability.day || start >= end) {
      notify('Working hours must have a valid start and a later end time.')
      return false
    }
    if (![15, 30, 60].includes(duration)) {
      notify('Appointment duration must be 15, 30, or 60 minutes.')
      return false
    }
    if ((breakStart === null) !== (breakEnd === null)) {
      notify('Set both break start and end times, or leave both blank.')
      return false
    }
    if (
      breakStart !== null &&
      (breakStart >= breakEnd || breakStart < start || breakEnd > end)
    ) {
      notify('The break must be inside working hours and end after it starts.')
      return false
    }

    const existingIndex = consultationAvailability.value.findIndex(
      (item) =>
        item.id === availability.id &&
        (item.doctorId ?? 'grace-miller') === selectedDoctorId.value,
    )
    const dayIndex = consultationAvailability.value.findIndex(
      (item) =>
        item.day === availability.day &&
        (item.doctorId ?? 'grace-miller') === selectedDoctorId.value,
    )
    const targetIndex = existingIndex === -1 ? dayIndex : existingIndex
    const updatedAvailability = {
      ...availability,
      doctorId: selectedDoctorId.value,
      id:
        targetIndex === -1
          ? `availability-${availability.day.toLowerCase()}`
          : consultationAvailability.value[targetIndex].id,
      duration,
    }
    if (targetIndex === -1) consultationAvailability.value.push(updatedAvailability)
    else consultationAvailability.value.splice(targetIndex, 1, updatedAvailability)
    return true
  }

  function removeAvailability(availabilityId) {
    consultationAvailability.value = consultationAvailability.value.filter(
      (availability) => availability.id !== availabilityId,
    )
  }

  function blockDate(date, reason = '') {
    if (!date || date < dateKey(new Date())) {
      notify('Choose today or a future date to block.')
      return false
    }
    if (
      appointments.value.some(
        (appointment) =>
          appointment.doctorId === selectedDoctorId.value &&
          appointment.dateKey === date &&
          ACTIVE_STATUSES.includes(appointment.status),
      )
    ) {
      notify('Resolve the appointments on this date before marking it unavailable.')
      return false
    }
    if (!unavailableDates.value.some((item) => item.date === date)) {
      unavailableDates.value.push({
        date,
        reason: reason.trim(),
        doctorId: selectedDoctorId.value,
      })
    }
    return true
  }

  function unblockDate(date) {
    unavailableDates.value = unavailableDates.value.filter(
      (item) => item.date !== date || item.doctorId !== selectedDoctorId.value,
    )
  }

  function sendMessage(text) {
    const message = text.trim()
    if (!message) return false
    chatMessages.value.push({
      id: Date.now(),
      from: 'doctor',
      text: message,
      time: new Intl.DateTimeFormat('en', { hour: 'numeric', minute: '2-digit' }).format(
        new Date(),
      ),
    })
    return true
  }

  function addPrescription(name, directions) {
    const medicine = name.trim()
    if (!medicine) return false
    prescriptions.value.unshift({ name: medicine, directions: directions.trim(), date: 'Today' })
    return true
  }

  function notify(message) {
    lastNotice.value = message
    window.clearTimeout(noticeTimeout)
    noticeTimeout = window.setTimeout(() => {
      if (lastNotice.value === message) lastNotice.value = ''
    }, 3500)
  }

  return {
    role,
    isDemoSession,
    doctors,
    appointments,
    consultationAvailability,
    unavailableDates,
    selectedAppointmentId,
    selectedDoctorId,
    selectedDate,
    selectedTime,
    reportTab,
    historyTab,
    messages,
    activeChat,
    chatMessages,
    prescriptions,
    patientProfile,
    doctorProfile,
    lastNotice,
    selectedDoctor,
    selectedAppointment,
    upcomingAppointments,
    signIn,
    signOut,
    chooseBooking,
    getAvailableTimes,
    validateAppointmentSlot,
    confirmBooking,
    updateAppointmentStatus,
    cancelAppointment,
    rescheduleAppointment,
    saveAvailability,
    removeAvailability,
    blockDate,
    unblockDate,
    sendMessage,
    addPrescription,
    notify,
  }
})
