import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, fileURLToPath(new URL('.', import.meta.url)), '')

  return {
    // Flask serves the built app under /app/ (app/routes/spa_routes.py). The dev server uses the
    // same base, so URLs, assets and the router behave identically in development and production.
    base: '/app/',
    plugins: [vue(), vueDevTools()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      // `npm run dev` -> open http://localhost:5173/app/ . The browser only ever talks to Vite;
      // /api is forwarded to Flask, so the session cookie and CSRF token work without CORS.
      proxy: {
        '/api': { target: env.BACKEND_URL || 'http://127.0.0.1:5000' },
      },
    },
    build: {
      // Flask sends `img-src 'self'`, which blocks data: URIs. Vite would otherwise inline
      // small images/SVGs as data: URIs, so keep every asset a real file.
      assetsInlineLimit: 0,
    },
  }
})
