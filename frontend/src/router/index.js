import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/PublicPage.vue'),
    meta: { page: 'home' },
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/PublicPage.vue'),
    meta: { page: 'about' },
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('../views/PublicPage.vue'),
    meta: { page: 'contact' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/AuthPage.vue'),
    meta: { page: 'login' },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/AuthPage.vue'),
    meta: { page: 'register-patient' },
  },
  {
    path: '/register/doctor',
    name: 'register-doctor',
    component: () => import('../views/AuthPage.vue'),
    meta: { page: 'register-doctor' },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('../views/AuthPage.vue'),
    meta: { page: 'forgot-password' },
  },
  {
    path: '/patient',
    name: 'patient-dashboard',
    component: () => import('../views/PatientDashboard.vue'),
  },
  {
    path: '/doctor',
    name: 'doctor-dashboard',
    component: () => import('../views/DoctorDashboard.vue'),
  },
  {
    path: '/appointments/new',
    name: 'appointment-booking',
    component: () => import('../views/AppointmentPage.vue'),
  },
  {
    path: '/patient/reports',
    name: 'patient-reports',
    component: () => import('../views/ReportsPage.vue'),
  },
  {
    path: '/doctor/patients/:id/history',
    name: 'patient-history',
    component: () => import('../views/PatientHistoryPage.vue'),
  },
  {
    path: '/doctor/chat',
    name: 'doctor-chat',
    component: () => import('../views/DoctorChatPage.vue'),
  },
  {
    path: '/patient/profile',
    name: 'patient-profile',
    component: () => import('../views/ProfilePage.vue'),
    meta: { role: 'patient' },
  },
  {
    path: '/doctor/profile',
    name: 'doctor-profile',
    component: () => import('../views/ProfilePage.vue'),
    meta: { role: 'doctor' },
  },
  {
    path: '/appointments/confirmed',
    name: 'appointment-confirmed',
    component: () => import('../views/AppointmentPage.vue'),
    meta: { state: 'confirmed' },
  },
  {
    path: '/appointments/cancel',
    name: 'appointment-cancel',
    component: () => import('../views/AppointmentPage.vue'),
    meta: { state: 'cancel' },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

export default router
