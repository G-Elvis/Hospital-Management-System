// The API speaks ISO strings ("2026-11-02", "2026-11-02T09:30", "09:30"); the UI shows
// friendly text. Dates are handled as "date keys" (YYYY-MM-DD) to avoid time-zone surprises.

export function toDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function parseDateKey(dateKey) {
  return new Date(`${dateKey}T00:00:00`)
}

export function formatDate(dateKey) {
  if (!dateKey) return ''
  return new Intl.DateTimeFormat('en', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(parseDateKey(dateKey))
}

/** "09:30" -> "9:30am" */
export function formatTime(time) {
  if (!time) return ''
  const [hour, minute] = time.split(':').map(Number)
  return `${hour % 12 || 12}:${String(minute).padStart(2, '0')}${hour < 12 ? 'am' : 'pm'}`
}

/** "2026-11-02T09:30" -> { dateKey: "2026-11-02", time: "09:30" } */
export function splitStart(startTime) {
  const [dateKey, time = ''] = startTime.split('T')
  return { dateKey, time: time.slice(0, 5) }
}

export function isSunday(dateKey) {
  return parseDateKey(dateKey).getDay() === 0
}

export function currentTime(now = new Date()) {
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

/** "dr_ann" -> "DA", "reception" -> "R" (the API has usernames and names, never photos) */
export function initialsOf(name) {
  const parts = String(name || '')
    .split(/[^A-Za-z0-9]+/)
    .filter(Boolean)
  return (parts.length > 1 ? parts[0][0] + parts[1][0] : (parts[0] || '?')[0]).toUpperCase()
}
