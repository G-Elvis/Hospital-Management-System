import { ref } from 'vue'
import { defineStore } from 'pinia'

import { api } from '../services/apiClient'
import { currentTime, isSunday, splitStart, toDateKey } from '../utils/datetime'

function normaliseAppointment(item) {
  const { dateKey, time } = splitStart(item.start_time)
  return {
    id: item.id,
    patientId: item.patient_id,
    patientName: item.patient_name,
    doctorId: item.doctor_id,
    doctorName: item.doctor_name,
    dateKey,
    time,
    status: item.status, // Scheduled | Completed | Cancelled
  }
}

// Everything the screens show comes from the Flask API. Nothing is invented client-side.
export const useClinicStore = defineStore('clinic', () => {
  const doctors = ref([])
  const slots = ref([])
  const genders = ref([])
  const appointments = ref([])
  const lastBooking = ref(null)
  const notice = ref('')
  let noticeTimer

  function notify(message) {
    notice.value = message
    window.clearTimeout(noticeTimer)
    noticeTimer = window.setTimeout(() => {
      if (notice.value === message) notice.value = ''
    }, 4000)
  }

  // ---- reference data ----------------------------------------------------------------
  async function loadDoctors() {
    doctors.value = (await api.get('doctors')).doctors
  }

  async function loadSlots() {
    slots.value = (await api.get('slots')).slots // "09:00" ... "16:30"
  }

  async function loadGenders() {
    genders.value = (await api.get('genders')).genders
  }

  // ---- appointments ------------------------------------------------------------------
  async function loadAppointments() {
    // Receptionists get every appointment; the server limits a doctor to their own.
    appointments.value = (await api.get('appointments')).appointments.map(normaliseAppointment)
  }

  /** Free slots for a doctor on a day, mirroring the server's rules (the server has the last word). */
  function availableTimes(doctorId, dateKey, now = new Date()) {
    if (!doctorId || !dateKey || !slots.value.length) return []
    const today = toDateKey(now)
    if (dateKey < today || isSunday(dateKey)) return []
    const taken = new Set(
      appointments.value
        .filter(
          (item) =>
            item.doctorId === doctorId && item.dateKey === dateKey && item.status === 'Scheduled',
        )
        .map((item) => item.time),
    )
    return slots.value.filter(
      (time) => !taken.has(time) && !(dateKey === today && time <= currentTime(now)),
    )
  }

  async function bookAppointment({ patientId, doctorId, dateKey, time, patientName, doctorName }) {
    const { appointment_id: id } = await api.post('appointments', {
      patient_id: patientId,
      doctor_id: doctorId,
      date: dateKey,
      slot: time,
    })
    // Kept for the confirmation screen (names are display-only; the server stores the ids).
    lastBooking.value = { id, patientId, doctorId, dateKey, time, patientName, doctorName }
    await loadAppointments().catch(() => {})
    return lastBooking.value
  }

  async function cancelAppointment(id) {
    await api.post(`appointments/${id}/cancel`)
    await loadAppointments().catch(() => {})
  }

  async function completeAppointment(id) {
    await api.post(`appointments/${id}/complete`)
    await loadAppointments().catch(() => {})
  }

  // ---- patients ----------------------------------------------------------------------
  async function searchPatients(query = '') {
    return (await api.get(`patients?q=${encodeURIComponent(query)}`)).patients
  }

  async function getPatient(id) {
    return (await api.get(`patients/${id}`)).patient
  }

  async function registerPatient(form, confirmDuplicate = false) {
    const body = { ...form, confirm_duplicate: confirmDuplicate }
    return (await api.post('patients', body)).patient
  }

  // ---- medical records (doctors only) --------------------------------------------------
  async function loadRecords(patientId) {
    return (await api.get(`patients/${patientId}/records`)).records
  }

  async function addRecord(patientId, record) {
    await api.post(`patients/${patientId}/records`, record)
  }

  return {
    doctors,
    slots,
    genders,
    appointments,
    lastBooking,
    notice,
    notify,
    loadDoctors,
    loadSlots,
    loadGenders,
    loadAppointments,
    availableTimes,
    bookAppointment,
    cancelAppointment,
    completeAppointment,
    searchPatients,
    getPatient,
    registerPatient,
    loadRecords,
    addRecord,
  }
})
