<script setup>
import { reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import DashboardHeader from '../components/DashboardHeader.vue'
import { useCareSyncStore } from '../stores/careSync'

const route = useRoute()
const store = useCareSyncStore()
const form = reactive({ name: '', directions: '' })
const showPrescriptionForm = ref(false)
const tabs = ['Medical report', 'Test Results', 'Prescriptions']

watch(
  () => route.query.tab,
  (tab) => {
    if (tabs.includes(tab)) store.historyTab = tab
  },
  { immediate: true },
)

function addPrescription() {
  if (!store.addPrescription(form.name, form.directions)) {
    store.notify('Enter a medicine name before saving.')
    return
  }
  form.name = ''
  form.directions = ''
  showPrescriptionForm.value = false
  store.notify('Prescription added to the mock patient record.')
}
</script>

<template>
  <main class="dashboard-page">
    <DashboardHeader role="doctor" />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" to="/doctor">Back</RouterLink>
    </div>
    <div class="history-layout">
      <aside class="history-patient-card">
        <img :src="store.messages[0].photo" alt="Laura Aguirre" />
        <h2>Laura Aguirre</h2>
        <p>Initial visit</p>
        <span class="time-pill">12th September, 9:00am</span>
      </aside>
      <section class="history-main">
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab"
            type="button"
            :class="{ active: store.historyTab === tab }"
            @click="store.historyTab = tab"
          >
            {{ tab }}
          </button>
        </div>
        <section class="history-panel">
          <template v-if="store.historyTab === 'Prescriptions'">
            <h2>Prescriptions</h2>
            <article v-for="item in store.prescriptions" :key="item.name" class="prescription-row">
              <div>
                <strong>{{ item.name }}</strong
                ><small>{{ item.directions }}</small>
              </div>
              <b>{{ item.date }}</b>
            </article>
            <button
              v-if="!showPrescriptionForm"
              class="button button-primary add-prescription"
              type="button"
              @click="showPrescriptionForm = true"
            >
              Add prescription
            </button>
            <form v-else class="prescription-form" @submit.prevent="addPrescription">
              <label
                >Medicine<input v-model.trim="form.name" required placeholder="Add a medication"
              /></label>
              <label
                >Directions<input v-model.trim="form.directions" placeholder="Dosage and schedule"
              /></label>
              <div>
                <button class="button button-primary" type="submit">Save prescription</button
                ><button
                  class="button button-muted"
                  type="button"
                  @click="showPrescriptionForm = false"
                >
                  Cancel
                </button>
              </div>
            </form>
          </template>
          <template v-else-if="store.historyTab === 'Medical report'">
            <h2>Medical report</h2>
            <div class="record-box">
              <strong>Patient overview</strong>
              <p>Laura Aguirre · Initial visit</p>
              <p>Patient history and care notes are sample content in this frontend preview.</p>
            </div>
            <div class="record-box">
              <strong>Current care plan</strong>
              <p>Follow-up appointment scheduled for September 12th at 9:00am.</p>
            </div>
          </template>
          <template v-else>
            <h2>Test results</h2>
            <article
              v-for="result in ['Complete blood count', 'Lipid profile', 'Blood glucose test']"
              :key="result"
              class="record-box"
            >
              <strong>{{ result }}</strong
              ><span>September 9th · Reviewed</span>
            </article>
          </template>
        </section>
      </section>
    </div>
    <div v-if="store.lastNotice" class="toast" role="status">{{ store.lastNotice }}</div>
  </main>
</template>
