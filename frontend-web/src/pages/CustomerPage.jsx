import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { predict } from '../api'
import { CATEGORIES, COUNTRIES, SHIPPING_MODES } from '../data'
import { COUNTRY_MARKET } from '../countryMarket'

const EASE = [0.16, 1, 0.3, 1]

const MODE_NAMES = {
  'Same Day':       'Same Day',
  'First Class':    'First Class (express)',
  'Second Class':   'Second Class',
  'Standard Class': 'Standard Class (economy)',
}

const today = () => new Date().toISOString().slice(0, 10)

function addDays(isoDate, days) {
  const d = new Date(`${isoDate}T00:00:00`)
  d.setDate(d.getDate() + days)
  return d.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

function Result({ result }) {
  if (!result) {
    return (
      <div className="cust-result cust-result-empty">
        <div className="cust-result-label">Your estimate</div>
        <p>Fill in your order details and press <strong>Estimate shipping time</strong>.</p>
      </div>
    )
  }

  const days = Math.max(0, Math.round(result.days))
  return (
    <motion.div
      key={`${result.days}-${result.date}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: EASE }}
      className="cust-result"
    >
      <div className="cust-result-label">Estimated shipping time</div>
      <div className="cust-result-days">
        {days === 0 ? 'Same day' : <>{days} <span>{days === 1 ? 'day' : 'days'}</span></>}
      </div>
      <div className="cust-result-arrival">
        Expected to ship by <strong>{addDays(result.date, days)}</strong>
      </div>
    </motion.div>
  )
}

export default function CustomerPage() {
  const [fields, setFields] = useState({
    shipping_mode: 'Standard Class',
    order_country: 'Estados Unidos',
    category_name: CATEGORIES.includes('Cleats') ? 'Cleats' : CATEGORIES[0],
    quantity:      1,
    order_date:    today(),
  })
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  const set = (key) => (e) => setFields(f => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await predict({
        ...fields,
        market:           COUNTRY_MARKET[fields.order_country],
        customer_segment: 'Consumer',
      })
      setResult({ days: res.predicted_days, date: fields.order_date })
    } catch {
      setError('We could not calculate an estimate right now. Please try again in a moment.')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container" style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem 1.5rem 4rem' }}>
      {/* Banner */}
      <motion.section
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: EASE }}
        className="page-hero cust-hero"
      >
        <div className="cust-hero-text">
          <div className="eda-hero-eyebrow">Customer shipping estimate</div>
          <h1 className="cust-hero-title">When will my order <span className="accent">ship?</span></h1>
          <p className="cust-hero-sub">
            Tell us a little about your order and we will estimate how many days it will take to ship.
          </p>
        </div>
        <div className="cust-hero-media">
          <img src="/port-logistics.gif" alt="Illustration of a cargo ship being loaded at a port" />
        </div>
      </motion.section>

      {/* Form + result */}
      <div className="cust-grid">
        <form className="card cust-form" onSubmit={handleSubmit}>
          <h2 className="cust-form-title">Your order</h2>

          <div>
            <label className="form-label" htmlFor="c-mode">Delivery option</label>
            <select id="c-mode" className="form-select" value={fields.shipping_mode} onChange={set('shipping_mode')}>
              {SHIPPING_MODES.map(m => <option key={m} value={m}>{MODE_NAMES[m] ?? m}</option>)}
            </select>
          </div>

          <div>
            <label className="form-label" htmlFor="c-country">Delivery country</label>
            <select id="c-country" className="form-select" value={fields.order_country} onChange={set('order_country')}>
              {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div>
            <label className="form-label" htmlFor="c-cat">Product</label>
            <select id="c-cat" className="form-select" value={fields.category_name} onChange={set('category_name')}>
              {CATEGORIES.map(c => <option key={c} value={c}>{c.trim()}</option>)}
            </select>
          </div>

          <div className="cust-row">
            <div>
              <label className="form-label" htmlFor="c-qty">Quantity</label>
              <select id="c-qty" className="form-select" value={fields.quantity} onChange={set('quantity')}>
                {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label" htmlFor="c-date">Order date</label>
              <input id="c-date" type="date" className="form-input" value={fields.order_date} onChange={set('order_date')} required />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Calculating…' : 'Estimate shipping time'}
          </button>
        </form>

        <div className="cust-side">
          <AnimatePresence mode="wait">
            {error
              ? <motion.div key="err" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="cust-result cust-result-error">{error}</motion.div>
              : <Result key="res" result={result} />}
          </AnimatePresence>
          <p className="cust-note">
            Estimates are based on thousands of past DataCo orders and may vary.
          </p>
        </div>
      </div>
    </div>
  )
}
