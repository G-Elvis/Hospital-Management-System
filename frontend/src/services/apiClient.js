const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

export async function apiRequest(path, options = {}) {
  if (!apiBaseUrl) {
    throw new Error('VITE_API_BASE_URL is not configured.')
  }

  const url = new URL(path.replace(/^\/+/, ''), `${apiBaseUrl.replace(/\/+$/, '')}/`)
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}.`)
  }

  if (response.status === 204) return null
  return response.json()
}
