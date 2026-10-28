// Thin client for the Flask JSON API (app/routes/api_routes.py).
//
// * Same origin by default: in production Flask serves this app, and in development Vite proxies
//   /api to Flask (vite.config.js), so the session cookie travels with every request. Set
//   VITE_API_BASE_URL only if the API really lives somewhere else (it would then need CORS).
// * Flask rejects every POST that lacks the session's CSRF token, so the token that comes with
//   the session payload is remembered here and sent as `X-CSRF-Token`.
// * Failures become ApiError with the server's own message, ready to show to the user.

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/+$/, '')
const MUTATING = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export class ApiError extends Error {
  constructor(message, status = 0, errors = []) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.errors = errors // field-level messages from validation failures (HTTP 400)
  }
}

let csrfToken = ''
let onUnauthorized = () => {}

export function setCsrfToken(token) {
  csrfToken = token || ''
}

/** Called when a request comes back 401 (not logged in, or the session timed out). */
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

async function readJson(response) {
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return null // e.g. an HTML error page from a proxy
  }
}

async function send(path, { method = 'GET', body } = {}) {
  const headers = { Accept: 'application/json' }
  const init = { method, headers, credentials: 'same-origin' }
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    init.body = JSON.stringify(body)
  }
  if (MUTATING.has(method) && csrfToken) headers['X-CSRF-Token'] = csrfToken

  let response
  try {
    response = await fetch(`${API_BASE}/${path.replace(/^\/+/, '')}`, init)
  } catch {
    throw new ApiError('Cannot reach the server. Check your connection and try again.')
  }
  return { response, data: await readJson(response) }
}

/** Fetch the session (current user + a CSRF token) and remember the token. */
export async function refreshSession() {
  const { response, data } = await send('session')
  if (!response.ok || !data) throw new ApiError('Could not start a session.', response.status)
  setCsrfToken(data.csrf_token)
  return data
}

export async function apiRequest(path, options = {}) {
  const mutating = MUTATING.has(options.method || 'GET')
  if (mutating && !csrfToken) await refreshSession()

  let attempt = await send(path, options)

  // A 400 can mean "CSRF token no longer matches" (the 15-minute session expired and the cookie
  // was replaced). If a fresh token differs from the one we sent, retry once with it.
  if (mutating && attempt.response.status === 400 && !attempt.data?.errors) {
    const stale = csrfToken
    await refreshSession().catch(() => {})
    if (csrfToken && csrfToken !== stale) attempt = await send(path, options)
  }

  const { response, data } = attempt
  if (response.ok) return data

  const error = new ApiError(
    data?.error || `Request failed (status ${response.status}).`,
    response.status,
    data?.errors || [],
  )
  if (response.status === 401) onUnauthorized(error)
  throw error
}

export const api = {
  get: (path) => apiRequest(path),
  post: (path, body) => apiRequest(path, { method: 'POST', body }),
}
