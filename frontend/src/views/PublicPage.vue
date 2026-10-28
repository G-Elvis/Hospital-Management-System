<script setup>
import { computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useClinicStore } from '../stores/clinic'
import PublicHeader from '../components/PublicHeader.vue'
import BrandMark from '../components/BrandMark.vue'
import heroImage from '../assets/figma/care-hero.png'
import teamOne from '../assets/figma/doctor-grace.png'
import teamTwo from '../assets/figma/doctor-jake.png'
import teamThree from '../assets/figma/doctor-laura.png'

const route = useRoute()
const auth = useAuthStore()
const store = useClinicStore()
const page = computed(() => route.meta.page)
const contact = reactive({ name: '', email: '', message: '', audience: 'Patient' })

function sendContact() {
  store.notify('Your message is ready. Contact form submission is demo-only.')
  contact.name = ''
  contact.email = ''
  contact.message = ''
}
</script>

<template>
  <div class="public-page">
    <PublicHeader />

    <main v-if="page === 'home'" class="landing-content">
      <section class="landing-intro">
        <h1>WELCOME TO CARESYNC</h1>
        <p>Where healthcare is made accessible and manageable</p>
      </section>
      <section class="landing-hero">
        <img :src="heroImage" alt="A doctor caring for a patient" />
        <div class="landing-copy">
          <p>A platform where you can manage appointments, patients and healthcare services.</p>
          <RouterLink class="button button-primary hero-cta" :to="auth.home || '/login'">{{
            auth.home ? 'Go to dashboard' : 'Log in'
          }}</RouterLink>
        </div>
      </section>
    </main>

    <main v-else-if="page === 'about'" class="about-content">
      <img
        class="about-hero"
        :src="heroImage"
        alt="Healthcare professional checking a patient's blood pressure"
      />
      <section class="about-story">
        <span class="eyebrow">Who we are</span>
        <h1>Care that connects.<br />Confidence that lasts.</h1>
        <p>
          CareSync brings patients and healthcare professionals together in one thoughtfully
          designed space — making everyday care easier to navigate, coordinate and understand.
        </p>
      </section>
      <section class="purpose-panel">
        <div>
          <span class="eyebrow">Our purpose</span>
          <h2>Making healthcare feel simpler, more personal and more accessible.</h2>
          <p>
            From booking appointments to accessing health information, CareSync is designed to
            reduce friction and help people focus on what matters most: better care.
          </p>
        </div>
        <div class="approach-panel">
          <strong>01 &nbsp; CLARITY</strong>
          <p>A more organised healthcare journey</p>
          <strong>02 &nbsp; CONNECTION</strong>
          <p>Patients and providers in sync</p>
          <div class="team-avatars">
            <img :src="teamOne" alt="Care team member" />
            <img :src="teamTwo" alt="Care team member" />
            <img :src="teamThree" alt="Care team member" />
          </div>
        </div>
      </section>
      <section class="approach-cards">
        <article>
          <span>01</span>
          <h2>Care made clear</h2>
          <p>Keep appointments and health information together.</p>
        </article>
        <article>
          <span>02</span>
          <h2>People come first</h2>
          <p>Simple tools support the conversations that matter.</p>
        </article>
        <article>
          <span>03</span>
          <h2>Better connected</h2>
          <p>Patients and professionals can stay on the same page.</p>
        </article>
      </section>
    </main>

    <main v-else class="contact-content">
      <span class="eyebrow">Contact CareSync</span>
      <h1>Let’s start a conversation.</h1>
      <p class="contact-lead">
        Have a question, suggestion or need assistance? Send us a message and our team will be happy
        to help.
      </p>
      <div class="contact-grid">
        <section class="contact-details panel">
          <h2>We’re here to help.</h2>
          <p>
            Whether you are a patient or a healthcare professional, we would love to hear from you.
          </p>
          <div class="team-avatars">
            <img :src="teamOne" alt="Care team member" />
            <img :src="teamTwo" alt="Care team member" />
            <img :src="teamThree" alt="Care team member" />
          </div>
          <hr />
          <strong class="eyebrow">What to expect</strong>
          <p class="expect-copy">
            A clear, helpful response from our support team. Please avoid including sensitive
            medical information in your message.
          </p>
          <dl>
            <dt>Email</dt>
            <dd>support@caresync.com</dd>
            <dt>Phone</dt>
            <dd>+000 000 000 000</dd>
            <dt>Hours</dt>
            <dd>Mon - Fri, 8:00am - 5:00pm</dd>
          </dl>
        </section>
        <form class="contact-form panel" @submit.prevent="sendContact">
          <h2>Send us a message</h2>
          <div class="audience-picker">
            <span>I am a</span>
            <button
              type="button"
              :class="{ selected: contact.audience === 'Patient' }"
              @click="contact.audience = 'Patient'"
            >
              Patient
            </button>
            <button
              type="button"
              :class="{ selected: contact.audience === 'Doctor' }"
              @click="contact.audience = 'Doctor'"
            >
              Doctor
            </button>
          </div>
          <div class="contact-fields">
            <label
              >Full name<input v-model.trim="contact.name" required autocomplete="name"
            /></label>
            <label
              >Email address<input
                v-model.trim="contact.email"
                required
                type="email"
                autocomplete="email"
            /></label>
            <label class="message-field"
              >Your message<textarea v-model.trim="contact.message" required rows="4"></textarea>
            </label>
          </div>
          <button class="button button-primary" type="submit">Send message</button>
        </form>
      </div>
    </main>

    <footer v-if="page !== 'contact'" class="public-footer">
      <BrandMark />
      <nav aria-label="Footer navigation">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/about">About</RouterLink>
        <RouterLink to="/contact">Contact</RouterLink>
        <RouterLink to="/login">Log in</RouterLink>
      </nav>
      <span>© 2026 CareSync</span>
    </footer>
    <div v-if="store.notice" class="toast" role="status">{{ store.notice }}</div>
  </div>
</template>
