import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import OrderForm from '../components/OrderForm'
import ResultPanel from '../components/ResultPanel'
import ModelInfo from '../components/ModelInfo'
import { predictCombined, checkHealth } from '../api'

const HERO_STATS = [
  { value: '172,765', label: 'Order items analysed' },
  { value: '54.8%',   label: 'Historical late rate' },
  { value: '0.773',   label: 'Classifier ROC-AUC' },
  { value: '0.94 d',  label: 'Average error (days)' },
]

function Hero() {
  return (
    <motion.section
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="page-hero logi-hero"
    >
      <div className="logi-hero-photo" style={{ backgroundImage: 'url(/logistics-network.jpg)' }} />
      <div className="logi-hero-content">
        <p className="eda-hero-eyebrow" style={{ margin: '0 0 0.7rem' }}>Logistics · Delivery risk analysis</p>
        <h1 className="logi-hero-title">Delivery <span className="accent">Risk</span> Prediction</h1>
        <p className="logi-hero-sub">
          Assess each order at the moment it is placed: the probability of late delivery and the
          estimated number of shipping days.
        </p>
        <dl className="logi-stats">
          {HERO_STATS.map(s => (
            <div key={s.label} className="logi-stat">
              <dt>{s.label}</dt>
              <dd>{s.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </motion.section>
  )
}

export default function PredictionPage() {
  const [prediction,      setPrediction]      = useState(null)
  const [classification,  setClassification]  = useState(null)
  const [loading,         setLoading]         = useState(false)
  const [error,           setError]           = useState(null)
  const [lastFields,      setLastFields]      = useState(null)
  const [apiStatus,       setApiStatus]       = useState(null)

  useEffect(() => {
    checkHealth().then(ok => setApiStatus(ok))
  }, [])

  const handleSubmit = async (fields) => {
    setLoading(true)
    setError(null)
    setPrediction(null)
    setClassification(null)

    try {
      const combined = await predictCombined(fields)
      setPrediction(combined.regression)
      setClassification(combined.classification)
      setLastFields(fields)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ background: '#f1f5f9' }}>
      <div style={{
        maxWidth: 1300,
        margin: '0 auto',
        padding: '2rem 1.5rem 4rem',
      }} className="page-container">
        <Hero />

        {/* API warning */}
        {apiStatus === false && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              marginBottom: '1.25rem', padding: '0.75rem 1rem',
              background: '#fffbeb', border: '1px solid #fde68a',
              borderRadius: 10, fontSize: '0.8rem', color: '#92400e', fontWeight: 500,
            }}
          >
            API not reachable — start it with:{' '}
            <code style={{
              background: '#fef3c7', borderRadius: 5,
              padding: '1px 6px', fontFamily: 'monospace',
            }}>make api</code>
          </motion.div>
        )}

        {/* Two-column predictor */}
        <div className="pred-grid" style={{
          display: 'grid',
          gridTemplateColumns: '1.15fr 0.85fr',
          gap: '1.5rem',
          alignItems: 'start',
        }}>
          <OrderForm onSubmit={handleSubmit} loading={loading} />
          <ResultPanel prediction={prediction} classification={classification} loading={loading} error={error} lastFields={lastFields} />
        </div>

        <ModelInfo />
      </div>
    </div>
  )
}
