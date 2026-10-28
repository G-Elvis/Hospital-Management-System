<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import DashboardHeader from '../components/DashboardHeader.vue'
import InitialsAvatar from '../components/InitialsAvatar.vue'
import { useClinicStore } from '../stores/clinic'
import { formatDate } from '../utils/datetime'

const route = useRoute()
const clinic = useClinicStore()
const patientId = Number(route.params.id)

const tabs = ['Medical records', 'Prescriptions']
const activeTab = ref(tabs.includes(route.query.tab) ? route.query.tab : tabs[0])
const patient = ref(null)
const records = ref([])
const loading = ref(true)
const loadError = ref('')
const showForm = ref(false)
const form = reactive({ diagnosis: '', treatment: '', prescription: '' })
const errors = ref([])
const busy = ref(false)

const prescriptions = computed(() => records.value.filter((item) => item.prescription))

// "2026-11-02T09:30" -> "2 November 2026, 09:30"
function when(createdAt) {
  const [date, time] = createdAt.split('T')
  return `${formatDate(date)}, ${time}`
}

async function load() {
  records.value = await clinic.loadRecords(patientId)
}

async function addRecord() {
  errors.value = []
  busy.value = true
  try {
    await clinic.addRecord(patientId, { ...form })
    await load()
    form.diagnosis = form.treatment = form.prescription = ''
    showForm.value = false
    clinic.notify('Record added to the patient’s history.')
  } catch (failure) {
    errors.value = failure.errors.length ? failure.errors : [failure.message]
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    ;[patient.value] = await Promise.all([clinic.getPatient(patientId), load()])
  } catch (failure) {
    loadError.value = failure.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="dashboard-page">
    <DashboardHeader />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" to="/doctor">Back</RouterLink>
    </div>
    <p v-if="loading" class="empty-state">Loading…</p>
    <p v-else-if="loadError" class="form-error" role="alert">{{ loadError }}</p>
    <div v-else class="history-layout">
      <aside class="history-patient-card">
        <InitialsAvatar :name="patient.full_name" :size="92" />
        <h2>{{ patient.full_name }}</h2>
        <p>{{ patient.gender }} · born {{ formatDate(patient.date_of_birth) }}</p>
        <span class="time-pill">{{ patient.phone }}</span>
      </aside>
      <section class="history-main">
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab"
            type="button"
            :class="{ active: activeTab === tab }"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </div>
        <section class="history-panel">
          <template v-if="activeTab === 'Medical records'">
            <h2>Medical records</h2>
            <article v-for="record in records" :key="record.id" class="record-box">
              <strong>{{ record.diagnosis }}</strong>
              <span>{{ when(record.created_at) }} · {{ record.doctor_name }}</span>
              <p v-if="record.treatment">Treatment: {{ record.treatment }}</p>
            </article>
            <p v-if="!records.length" class="empty-state">No records yet for this patient.</p>
          </template>
          <template v-else>
            <h2>Prescriptions</h2>
            <article v-for="record in prescriptions" :key="record.id" class="prescription-row">
              <div>
                <strong>{{ record.prescription }}</strong
                ><small>For {{ record.diagnosis }} · {{ record.doctor_name }}</small>
              </div>
              <b>{{ when(record.created_at) }}</b>
            </article>
            <p v-if="!prescriptions.length" class="empty-state">No prescriptions recorded.</p>
          </template>
          <button
            v-if="!showForm"
            class="button button-primary add-prescription"
            type="button"
            @click="showForm = true"
          >
            Add record
          </button>
          <form v-else class="prescription-form record-form" @submit.prevent="addRecord">
            <label
              >Diagnosis<input v-model.trim="form.diagnosis" required maxlength="5000"
            /></label>
            <label
              >Treatment<textarea v-model.trim="form.treatment" rows="2" maxlength="5000" />
            </label>
            <label
              >Prescription<textarea v-model.trim="form.prescription" rows="2" maxlength="5000" />
            </label>
            <ul v-if="errors.length" class="form-errors" role="alert">
              <li v-for="message in errors" :key="message">{{ message }}</li>
            </ul>
            <div>
              <button class="button button-primary" type="submit" :disabled="busy">
                {{ busy ? 'Saving…' : 'Save record' }}</button
              ><button class="button button-muted" type="button" @click="showForm = false">
                Cancel
              </button>
            </div>
          </form>
        </section>
      </section>
    </div>
    <div v-if="clinic.notice" class="toast" role="status">{{ clinic.notice }}</div>
  </main>
</template>