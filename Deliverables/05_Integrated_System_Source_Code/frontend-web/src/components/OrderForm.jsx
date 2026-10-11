import { useState } from 'react'
import { motion } from 'framer-motion'
import { SHIPPING_MODES, SEGMENTS, MARKETS, CATEGORIES, COUNTRIES } from '../data'

const today = new Date().toISOString().split('T')[0]

function Spinner() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         strokeWidth="2.5" strokeLinecap="round"
         style={{ animation: 'spin 0.8s linear infinite' }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" opacity="0.35"/>
      <path d="M12 2v4"/>
    </svg>
  )
}

const MODE_META = {
  'Same Day':       { icon: '⚡', color: '#0891b2', days: 0, desc: 'Same-day fulfilment' },
  'First Class':    { icon: '🚀', color: '#4f46e5', days: 1, desc: '1-day scheduled window' },
  'Second Class':   { icon: '📬', color: '#7c3aed', days: 2, desc: '2-day scheduled window' },
  'Standard Class': { icon: '📦', color: '#64748b', days: 4, desc: '4-day scheduled window' },
}

function ShippingPreview({ mode }) {
  const m = MODE_META[mode]
  if (!m) return null
  return (
    <div style={{
      marginTop: 7, display: 'flex', alignItems: 'center', gap: 8,
      background: '#f8fafc', border: '1px solid #e2e8f0',
      borderRadius: 8, padding: '0.4rem 0.75rem',
      fontSize: '0.75rem', color: '#64748b',
    }}>
      <span style={{ fontSize: '1rem' }}>{m.icon}</span>
      <span>{m.desc} —</span>
      <span style={{ color: m.color, fontWeight: 700 }}>
        {m.days === 0 ? '0 days (same day)' : `${m.days} day${m.days !== 1 ? 's' : ''} scheduled`}
      </span>
    </div>
  )
}

export default function OrderForm({ onSubmit, loading }) {
  const [fields, setFields] = useState({
    shipping_mode:    'Standard Class',
    customer_segment: 'Consumer',
    market:           'LATAM',
    order_country:    'Estados Unidos',
    category_name:    'Fishing',
    quantity:         1,
    order_date:       today,
  })

  const set = (key) => (e) =>
    setFields(f => ({ ...f, [key]: e.target.value }))

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(fields)
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      className="card"
      style={{ padding: '1.75rem' }}
    >
      <div className="section-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
             strokeLinecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        Order Details
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

        {/* Shipping mode */}
        <div>
          <label className="form-label">
            Shipping Mode
            <span style={{ color: '#6366f1', marginLeft: 6, fontWeight: 700, fontSize: '0.6rem',
                           background: '#eef2ff', border: '1px solid #c7d2fe',
                           borderRadius: 4, padding: '1px 5px' }}>
              strongest predictor
            </span>
          </label>
          <select className="form-select" value={fields.shipping_mode} onChange={set('shipping_mode')}>
            {SHIPPING_MODES.map(m => <option key={m}>{m}</option>)}
          </select>
          <ShippingPreview mode={fields.shipping_mode} />
        </div>

        {/* Row: segment + market */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div>
            <label className="form-label">Customer Segment</label>
            <select className="form-select" value={fields.customer_segment} onChange={set('customer_segment')}>
              {SEGMENTS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="form-label">Market / Region</label>
            <select className="form-select" value={fields.market} onChange={set('market')}>
              {MARKETS.map(m => <option key={m}>{m}</option>)}
            </select>
          </div>
        </div>

        {/* Row: country + category */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div>
            <label className="form-label">Order Country</label>
            <select className="form-select" value={fields.order_country} onChange={set('order_country')}>
              {COUNTRIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="form-label">Product Category</label>
            <select className="form-select" value={fields.category_name} onChange={set('category_name')}>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
        </div>

        {/* Row: quantity + date */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div>
            <label className="form-label">
              Item Quantity
              <span style={{ color: '#94a3b8', marginLeft: 4, fontWeight: 500, textTransform: 'none', fontSize: '0.62rem' }}>(1–5)</span>
            </label>
            <input type="number" min={1} max={5} className="form-input"
                   value={fields.quantity} onChange={set('quantity')} />
          </div>
          <div>
            <label className="form-label">Order Date</label>
            <input type="date" className="form-input"
                   value={fields.order_date} onChange={set('order_date')} />
          </div>
        </div>

        {/* Submit */}
        <button type="submit" className="btn-primary" disabled={loading}
                style={{ marginTop: '0.25rem' }}>
          {loading
            ? <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <Spinner /> Running prediction…
              </span>
            : 'Predict Delivery Risk'}
        </button>
      </form>

      <p style={{
        marginTop: '0.9rem', fontSize: '0.7rem', color: '#94a3b8', lineHeight: 1.55,
        paddingLeft: '0.75rem', borderLeft: '2px solid #e2e8f0',
      }}>
        Country names match the original DataCo dataset (Spanish labels). The model extracts
        weekday, month, quarter, and hour from the order date automatically.
      </p>
    </motion.div>
  )
}
