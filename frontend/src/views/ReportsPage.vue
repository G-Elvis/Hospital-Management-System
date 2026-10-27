<script setup>
import { ref } from 'vue'
import DashboardHeader from '../components/DashboardHeader.vue'
import { useCareSyncStore } from '../stores/careSync'

const store = useCareSyncStore()
const tabs = ['Medical reports', 'Lab results', 'Image reports']
const selectedReport = ref('')
const reports = [
  {
    title: 'Complete blood count',
    doctor: 'Dr. Grace Miller, Cardiologist',
    date: 'September 9th',
    tab: 'Lab results',
  },
  {
    title: 'Lipid profile',
    doctor: 'Dr. Grace Miller, Cardiologist',
    date: 'September 2nd',
    tab: 'Lab results',
  },
  {
    title: 'Blood glucose test',
    doctor: 'Dr. Jake Alexandra, Psychologist',
    date: 'August 20th',
    tab: 'Lab results',
  },
  {
    title: 'Chest X-ray',
    doctor: 'Dr. Grace Miller, Cardiologist',
    date: 'August 12th',
    tab: 'Image reports',
  },
]

function openReport(title) {
  selectedReport.value = title
}
</script>

<template>
  <main class="dashboard-page reports-page">
    <DashboardHeader />
    <div class="dashboard-top-links">
      <RouterLink class="button button-muted" to="/patient">Back</RouterLink>
    </div>
    <h1>My medical reports</h1>
    <p class="subtle-text">Lab results and image reports from your doctors</p>
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        type="button"
        :class="{ active: store.reportTab === tab }"
        @click="store.reportTab = tab"
      >
        {{ tab }}
      </button>
    </div>
    <section class="report-list">
      <article
        v-for="report in reports.filter(
          (item) => store.reportTab === 'Medical reports' || item.tab === store.reportTab,
        )"
        :key="report.title"
        class="report-card"
      >
        <div>
          <h2>{{ report.title }}</h2>
          <p>Requested by {{ report.doctor }}</p>
        </div>
        <div class="report-date">
          <small>Date</small><strong>{{ report.date }}</strong>
        </div>
        <button class="button button-muted" type="button" @click="openReport(report.title)">
          View
        </button>
        <button
          class="button button-muted"
          type="button"
          @click="store.notify('Report download is not available in this demo.')"
        >
          Download
        </button>
      </article>
    </section>
    <div v-if="selectedReport" class="modal-backdrop" @click.self="selectedReport = ''">
      <section class="dialog-card" role="dialog" aria-modal="true" :aria-label="selectedReport">
        <button
          class="dialog-close"
          type="button"
          aria-label="Close report"
          @click="selectedReport = ''"
        >
          ×
        </button>
        <span class="eyebrow">Medical report</span>
        <h2>{{ selectedReport }}</h2>
        <p>This sample report is mock content for the CareSync frontend preview.</p>
        <button class="button button-primary" type="button" @click="selectedReport = ''">
          Close
        </button>
      </section>
    </div>
    <div v-if="store.lastNotice" class="toast" role="status">{{ store.lastNotice }}</div>
  </main>
</template>
