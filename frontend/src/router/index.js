import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'

// meta.roles   -> the page needs a logged-in user with one of these backend roles
// meta.guest   -> the page is for logged-out visitors (a logged-in user is sent to their home)
const RECEPTION = ['RECEPTIONIST']
const DOCTOR = ['DOCTOR']

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
    meta: { guest: true },
  },
  // Accounts are created by an administrator, so there is no self-registration or reset flow.
  { path: '/register', redirect: '/login' },
  { path: '/register/doctor', redirect: '/login' },
  { path: '/forgot-password', redirect: '/login' },

  // ---- reception ----
  {
    path: '/reception',
    name: 'reception-dashboard',
    component: () => import('../views/ReceptionDashboard.vue'),
    meta: { roles: RECEPTION },
  },
  {
    path: '/reception/patients/new',
    name: 'patient-register',
    component: () => import('../views/PatientRegisterPage.vue'),
    meta: { roles: RECEPTION },
  },
  {
    path: '/reception/profile',
    name: 'reception-profile',
    component: () => import('../views/ProfilePage.vue'),
    meta: { roles: RECEPTION },
  },
  {
    path: '/appointments/new',
    name: 'appointment-booking',
    component: () => import('../views/AppointmentPage.vue'),
    meta: { roles: RECEPTION },
  },
  {
    path: '/appointments/confirmed',
    name: 'appointment-confirmed',
    component: () => import('../views/AppointmentPage.vue'),
    meta: { roles: RECEPTION, state: 'confirmed' },
  },
  {
    path: '/appointments/cancel',
    name: 'appointment-cancel',
    component: () => import('../views/AppointmentPage.vue'),
    meta: { roles: RECEPTION, state: 'cancel' },
  },

  // ---- doctors ----
  {
    path: '/doctor',
    name: 'doctor-dashboard',
    component: () => import('../views/DoctorDashboard.vue'),
    meta: { roles: DOCTOR },
  },
  {
    path: '/doctor/profile',
    name: 'doctor-profile',
    component: () => import('../views/ProfilePage.vue'),
    meta: { roles: DOCTOR },
  },
  {
    path: '/doctor/patients/:id(\\d+)/history',
    name: 'patient-history',
    component: () => import('../views/PatientHistoryPage.vue'),
    meta: { roles: DOCTOR },
  },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  // BASE_URL is "/app/" (vite.config.js), the prefix Flask serves the app under.
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init() // restores the session from the cookie on first load / refresh

  if (to.meta.roles) {
    if (!auth.user) return { name: 'login', query: { redirect: to.fullPath } }
    if (!to.meta.roles.includes(auth.user.role)) return auth.home || '/'
  }
  if (to.meta.guest && auth.user && auth.home) return auth.home
  return true
})

export default router

