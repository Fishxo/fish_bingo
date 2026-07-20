export function formatMoney(value, { prefix = 'Br ', decimals = 2 } = {}) {
  const num = Number(value)
  if (Number.isNaN(num)) return `${prefix}0.00`
  return `${prefix}${num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })}`
}

export function formatDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  })
}

export function formatGameCode(gameId) {
  if (gameId == null) return '—'
  return `#${String(gameId).toUpperCase()}`
}
