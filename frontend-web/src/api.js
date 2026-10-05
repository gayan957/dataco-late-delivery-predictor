const BASE = '/api'

function buildBody(fields) {
  return JSON.stringify({
    shipping_mode:    fields.shipping_mode,
    market:           fields.market,
    order_country:    fields.order_country,
    category_name:    fields.category_name,
    quantity:         Number(fields.quantity),
    customer_segment: fields.customer_segment,
    order_date:       fields.order_date,
  })
}

async function post(url, fields) {
  const res = await fetch(`${BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: buildBody(fields),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `API error ${res.status}`)
  }
  return res.json()
}

export const predict        = (fields) => post('/predict',          fields)
export const classify       = (fields) => post('/classify',         fields)
export const predictCombined= (fields) => post('/predict/combined', fields)

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE}/health`, { signal: AbortSignal.timeout(2000) })
    return res.ok
  } catch {
    return false
  }
}
