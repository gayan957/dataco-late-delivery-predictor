import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import OrderForm from './components/OrderForm'
import ResultPanel from './components/ResultPanel'
import ModeComparison from './components/ModeComparison'
import ModelInfo from './components/ModelInfo'
import { predictCombined, predict, checkHealth } from './api'

const COMPARE_MODES = ['Same Day', 'First Class', 'Second Class', 'Standard Class']

const HERO_STATS = [
  { value: '180,519', label: 'Orders trained on' },
  { value: '54.8%',   label: 'Historical late rate' },
  { value: '5',       label: 'Models compared' },
  { value: 'MAE 0.96d', label: 'Best accuracy score' },
]

function Hero({ apiStatus }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: -28 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1] }}
      style={{
        position: 'relative',
        borderRadius: 24,
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #4338ca 0%, #7c3aed 55%, #1d4ed8 100%)',
        padding: '2.75rem 2.5rem 2.5rem',
        marginBottom: '2rem',
      }}
    >
      {/* Decorative circles */}
      <div style={{
        position: 'absolute', top: -90, right: -90,
        width: 340, height: 340, borderRadius: '50%',
        background: 'rgba(255,255,255,0.06)', pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', bottom: -70, left: '38%',
        width: 220, height: 220, borderRadius: '50%',
        background: 'rgba(255,255,255,0.04)', pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', top: 15, right: 220,
        width: 90, height: 90, borderRadius: '50%',
        background: 'rgba(255,255,255,0.07)', pointerEvents: 'none',
      }} />

      {/* Two-column: text left, van GIF right */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: '2rem' }}>

        {/* ── Left: text content ── */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Title row */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.2rem', marginBottom: '1rem' }}>
            <div style={{
              width: 58, height: 58, flexShrink: 0,
              background: 'rgba(255,255,255,0.15)',
              border: '1px solid rgba(255,255,255,0.22)',
              borderRadius: 16, display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: '1.8rem',
            }}>📦</div>

            <div style={{ flex: 1 }}>
              <h1 style={{
                color: '#ffffff', fontWeight: 900, fontSize: '1.9rem',
                margin: '0 0 5px', letterSpacing: '-0.03em', lineHeight: 1.1,
              }}>
                DataCo Delivery Predictor
              </h1>
              <p style={{
                color: 'rgba(255,255,255,0.65)', fontWeight: 600, fontSize: '0.7rem',
                textTransform: 'uppercase', letterSpacing: '0.1em', margin: 0,
              }}>
                IT3051 · Fundamentals of Data Mining · Group Mini-Project
              </p>
            </div>

            {apiStatus !== null && (
              <div style={{
                flexShrink: 0, display: 'flex', alignItems: 'center', gap: 6,
                background: 'rgba(255,255,255,0.12)',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: 20, padding: '0.4rem 0.9rem',
                fontSize: '0.7rem', color: 'rgba(255,255,255,0.9)', fontWeight: 600,
              }}>
                <span style={{
                  display: 'inline-block', width: 7, height: 7, borderRadius: '50%',
                  background: apiStatus ? '#4ade80' : '#f87171',
                  boxShadow: `0 0 6px ${apiStatus ? '#4ade80' : '#f87171'}`,
                }} />
                {apiStatus ? 'API Online' : 'API Offline'}
              </div>
            )}
          </div>

          {/* Description */}
          <p style={{
            color: 'rgba(255,255,255,0.85)', fontSize: '0.95rem',
            lineHeight: 1.65, margin: '0 0 1.6rem', maxWidth: 540,
          }}>
            Predict whether a supply chain order will arrive <strong style={{ color: '#fff' }}>late</strong> — at
            the moment it is placed. A Decision Tree trained on real DataCo logistics data.
            No post-delivery information used.
          </p>

          {/* Stats chips */}
          <div style={{ display: 'flex', gap: '0.7rem', flexWrap: 'wrap' }}>
            {HERO_STATS.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.12 + i * 0.07 }}
                style={{
                  background: 'rgba(255,255,255,0.12)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: 12, padding: '0.6rem 1.1rem',
                  minWidth: 100, textAlign: 'center',
                }}
              >
                <div style={{ color: '#fff', fontWeight: 900, fontSize: '1.1rem', lineHeight: 1 }}>
                  {s.value}
                </div>
                <div style={{
                  color: 'rgba(255,255,255,0.6)', fontSize: '0.6rem', fontWeight: 600,
                  marginTop: 3, textTransform: 'uppercase', letterSpacing: '0.06em',
                }}>
                  {s.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* ── Right: delivery van GIF ── */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          style={{
            flexShrink: 0,
            width: 480,
            height: 300,
            overflow: 'hidden',
            /* fade both left and right edges into the hero gradient */
            WebkitMaskImage: 'linear-gradient(to right, transparent 0%, black 18%, black 82%, transparent 100%)',
            maskImage:       'linear-gradient(to right, transparent 0%, black 18%, black 82%, transparent 100%)',
          }}
        >
          <img
            src="/delivery-van.gif"
            alt="Delivery van"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center',
              display: 'block',
            }}
          />
        </motion.div>

      </div>
    </motion.section>
  )
}

export default function App() {
  const [prediction,      setPrediction]      = useState(null)
  const [classification,  setClassification]  = useState(null)
  const [loading,         setLoading]         = useState(false)
  const [error,           setError]           = useState(null)
  const [lastFields,      setLastFields]      = useState(null)
  const [comparison,      setComparison]      = useState(null)
  const [apiStatus,       setApiStatus]       = useState(null)

  useEffect(() => {
    checkHealth().then(ok => setApiStatus(ok))
  }, [])

  const handleSubmit = async (fields) => {
    setLoading(true)
    setError(null)
    setPrediction(null)
    setClassification(null)
    setComparison(null)

    try {
      const [combined, comp] = await Promise.all([
        predictCombined(fields),
        Promise.all(COMPARE_MODES.map(mode => predict({ ...fields, shipping_mode: mode }))),
      ])
      setPrediction(combined.regression)
      setClassification(combined.classification)
      setLastFields(fields)
      setComparison(comp)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f1f5f9' }}>
      <div style={{
        maxWidth: 1300,
        margin: '0 auto',
        padding: '2rem 1.5rem 4rem',
      }}>
        <Hero apiStatus={apiStatus} />

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
            ⚠&nbsp; API not reachable — start it with:{' '}
            <code style={{
              background: '#fef3c7', borderRadius: 5,
              padding: '1px 6px', fontFamily: 'monospace',
            }}>make api</code>
          </motion.div>
        )}

        {/* Two-column predictor */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1.15fr 0.85fr',
          gap: '1.5rem',
          alignItems: 'start',
        }}>
          <OrderForm onSubmit={handleSubmit} loading={loading} />
          <ResultPanel prediction={prediction} classification={classification} loading={loading} error={error} lastFields={lastFields} />
        </div>

        {/* Mode comparison */}
        <AnimatePresence>
          {comparison && (
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            >
              <ModeComparison data={comparison} selectedMode={lastFields?.shipping_mode} />
            </motion.div>
          )}
        </AnimatePresence>

        <ModelInfo />
      </div>
    </div>
  )
}
