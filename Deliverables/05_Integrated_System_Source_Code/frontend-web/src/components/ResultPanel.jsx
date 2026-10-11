import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LATE_TIPS } from '../data'

/* ─────────────────────────────────────────────────────────────────────────
   RiskGauge — 270° arc showing classification probability (0 → 100 %)
   Same stroke-dasharray geometry as before; value is 0–1 fraction.
───────────────────────────────────────────────────────────────────────── */
function RiskGauge({ probability, isLate }) {
  const color = isLate ? '#ef4444' : '#22c55e'
  const fraction = Math.max(0.01, Math.min(0.99, probability))

  const cx = 150, cy = 130, r = 100
  const C        = 2 * Math.PI * r
  const trackLen = C * 0.75

  const [animFrac, setAnimFrac] = useState(0)
  const [numVal,   setNumVal]   = useState(0)
  const rafRef = useRef(null)

  useEffect(() => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    setAnimFrac(0); setNumVal(0)
    const dur = 1350, start = performance.now()
    const tick = (now) => {
      const p    = Math.min((now - start) / dur, 1)
      const ease = 1 - Math.pow(1 - p, 3)
      setAnimFrac(fraction * ease)
      setNumVal(probability * 100 * ease)
      if (p < 1) rafRef.current = requestAnimationFrame(tick)
      else { setAnimFrac(fraction); setNumVal(probability * 100) }
    }
    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [probability]) // eslint-disable-line react-hooks/exhaustive-deps

  const fillLen = Math.max(0.5, trackLen * animFrac)

  const dotAngle = (135 + animFrac * 270) * Math.PI / 180
  const dx = cx + r * Math.cos(dotAngle)
  const dy = cy + r * Math.sin(dotAngle)

  // Threshold marker at 65 %
  const threshFrac = 0.65
  const tAngle = (135 + threshFrac * 270) * Math.PI / 180
  const tmx = cx + (r + 3) * Math.cos(tAngle)
  const tmy = cy + (r + 3) * Math.sin(tAngle)
  const tlx = cx + (r + 22) * Math.cos(tAngle)
  const tly = cy + (r + 22) * Math.sin(tAngle)

  const a0 = 135 * Math.PI / 180
  const a1 = 45  * Math.PI / 180
  const off = r + 24

  return (
    <svg viewBox="0 0 300 240" style={{ width: '100%', maxWidth: 268, display: 'block', margin: '0 auto' }}>
      <defs>
        <linearGradient id="riskGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stopColor="#22c55e" />
          <stop offset="50%"  stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#ef4444" />
        </linearGradient>
      </defs>

      {/* Track */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e8f0" strokeWidth={22}
        strokeDasharray={`${trackLen} ${C - trackLen}`} strokeLinecap="round"
        transform={`rotate(135 ${cx} ${cy})`} />

      {/* Gradient hint */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="url(#riskGrad)" strokeWidth={22} strokeOpacity={0.14}
        strokeDasharray={`${trackLen} ${C - trackLen}`} strokeLinecap="round"
        transform={`rotate(135 ${cx} ${cy})`} />

      {/* Animated fill */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth={22}
        strokeDasharray={`${fillLen} ${C - fillLen}`} strokeLinecap="round"
        transform={`rotate(135 ${cx} ${cy})`} />

      {/* Threshold marker at 65 % */}
      <circle cx={+tmx.toFixed(1)} cy={+tmy.toFixed(1)} r={6} fill="#6366f1" />
      <text x={+tlx.toFixed(1)} y={+tly.toFixed(1)} textAnchor="middle" dominantBaseline="middle"
        fontSize={10} fill="#6366f1" fontWeight={700} fontFamily="Inter, system-ui, sans-serif">65%</text>

      {/* Dot at arc tip */}
      {animFrac > 0.02 && (
        <>
          <circle cx={+dx.toFixed(1)} cy={+dy.toFixed(1)} r={13} fill="white"
            style={{ filter: `drop-shadow(0 2px 6px ${color}55)` }} />
          <circle cx={+dx.toFixed(1)} cy={+dy.toFixed(1)} r={8} fill={color} />
        </>
      )}

      {/* Scale labels */}
      <text x={+(cx + off * Math.cos(a0)).toFixed(1)} y={+(cy + off * Math.sin(a0)).toFixed(1)}
        textAnchor="middle" dominantBaseline="middle"
        fontSize={11} fill="#94a3b8" fontWeight={600} fontFamily="Inter, system-ui, sans-serif">0%</text>
      <text x={+(cx + off * Math.cos(a1)).toFixed(1)} y={+(cy + off * Math.sin(a1)).toFixed(1)}
        textAnchor="middle" dominantBaseline="middle"
        fontSize={11} fill="#94a3b8" fontWeight={600} fontFamily="Inter, system-ui, sans-serif">100%</text>

      {/* Big % number */}
      <text x={cx} y={cy - 8} textAnchor="middle" dominantBaseline="middle"
        fontSize={54} fontWeight={900} fill={color} fontFamily="Inter, system-ui, sans-serif">
        {Math.round(numVal)}%
      </text>
      <text x={cx} y={cy + 24} textAnchor="middle" dominantBaseline="middle"
        fontSize={11} fill="#94a3b8" fontWeight={700} letterSpacing={3}
        fontFamily="Inter, system-ui, sans-serif">LATE RISK</text>

      {/* Verdict chip */}
      <rect x={cx - 50} y={cy + 44} width={100} height={22} rx={11}
        fill={isLate ? '#fef2f2' : '#f0fdf4'}
        stroke={isLate ? '#fecaca' : '#bbf7d0'} strokeWidth={1} />
      <text x={cx} y={cy + 55} textAnchor="middle" dominantBaseline="middle"
        fontSize={10} fill={isLate ? '#dc2626' : '#15803d'} fontWeight={700}
        fontFamily="Inter, system-ui, sans-serif">
        {isLate ? 'HIGH RISK' : 'LOW RISK'}
      </text>
    </svg>
  )
}

/* ── Metric tile ──────────────────────────────────────────────────────────── */
function MetricTile({ label, value, color, bg, border }) {
  return (
    <div className="metric-tile" style={{ background: bg, border: `1px solid ${border}` }}>
      <div style={{ fontSize: '1.2rem', fontWeight: 900, color, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: '0.6rem', color: '#94a3b8', fontWeight: 700,
                    textTransform: 'uppercase', letterSpacing: '0.07em', marginTop: 4 }}>
        {label}
      </div>
    </div>
  )
}

/* ── Regression days row ──────────────────────────────────────────────────── */
function RegressionRow({ prediction }) {
  const delta    = prediction.late_by
  const deltaStr = delta >= 0 ? `+${delta.toFixed(1)}d` : `${delta.toFixed(1)}d`
  const isLate   = prediction.is_late

  return (
    <div style={{
      background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 12,
      padding: '0.85rem 1rem', marginBottom: '0.85rem',
    }}>
      <div style={{
        fontSize: '0.62rem', fontWeight: 800, color: '#94a3b8',
        textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.6rem',
      }}>
        Regression Model · Days Estimate
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
        <MetricTile label="Predicted" value={`${prediction.predicted_days.toFixed(1)}d`}
          color="#4f46e5" bg="#eef2ff" border="#c7d2fe" />
        <MetricTile label="Scheduled" value={`${prediction.scheduled_days}d`}
          color="#475569" bg="#f8fafc" border="#e2e8f0" />
        <MetricTile label="Delta" value={deltaStr}
          color={isLate ? '#dc2626' : '#15803d'}
          bg={isLate ? '#fef2f2' : '#f0fdf4'}
          border={isLate ? '#fecaca' : '#bbf7d0'} />
      </div>
    </div>
  )
}

/* ── Placeholder ──────────────────────────────────────────────────────────── */
function Placeholder() {
  return (
    <motion.div key="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="card" style={{
        border: '1.5px dashed #c7d2fe', minHeight: 440,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: '2.5rem 2rem', textAlign: 'center',
      }}>
      <motion.div
        animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          width: 72, height: 72, borderRadius: 20, marginBottom: '1.25rem',
          background: '#eef2ff', border: '1px solid #c7d2fe',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem',
        }}>📊</motion.div>
      <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#334155', marginBottom: 6 }}>
        Awaiting Prediction
      </div>
      <div style={{ fontSize: '0.82rem', color: '#64748b', lineHeight: 1.65 }}>
        Fill in the order details on the left<br/>
        and click <strong style={{ color: '#4f46e5' }}>Predict Delivery Risk</strong>
      </div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', justifyContent: 'center', marginTop: '1.5rem' }}>
        {[
          ['Classifier · ROC-AUC 0.77', '#15803d', '#f0fdf4', '#bbf7d0'],
          ['Precision 89.4%',           '#7c3aed', '#f5f3ff', '#ddd6fe'],
          ['Regression · MAE 0.96d',    '#4f46e5', '#eef2ff', '#c7d2fe'],
        ].map(([t, c, bg, br]) => (
          <span key={t} style={{
            background: bg, border: `1px solid ${br}`,
            borderRadius: 8, padding: '0.3rem 0.75rem',
            fontSize: '0.68rem', fontWeight: 600, color: c,
          }}>{t}</span>
        ))}
      </div>
    </motion.div>
  )
}

/* ── Loading ──────────────────────────────────────────────────────────────── */
function LoadingState() {
  return (
    <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="card" style={{
        minHeight: 440, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', padding: '2rem',
      }}>
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.9, repeat: Infinity, ease: 'linear' }}
        style={{ width: 44, height: 44, borderRadius: '50%', marginBottom: '1.2rem',
                 border: '3px solid #e2e8f0', borderTop: '3px solid #4f46e5' }} />
      <div style={{ fontSize: '0.9rem', color: '#334155', fontWeight: 600 }}>Running both models…</div>
      <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 4 }}>
        Classifier + Regression in parallel
      </div>
    </motion.div>
  )
}

/* ── Error ────────────────────────────────────────────────────────────────── */
function ErrorState({ message }) {
  return (
    <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="card" style={{
        minHeight: 440, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: '2rem', textAlign: 'center', border: '1px solid #fecaca',
      }}>
      <div style={{ width: 56, height: 56, borderRadius: 16, background: '#fef2f2',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1.75rem', marginBottom: '1rem' }}>⚡</div>
      <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#dc2626', marginBottom: 8 }}>
        API Unreachable
      </div>
      <div style={{ fontSize: '0.8rem', color: '#64748b', lineHeight: 1.6, maxWidth: 250 }}>
        {message}<br /><br />Start the backend:
      </div>
      <code style={{ marginTop: 10, padding: '0.5rem 1.1rem', borderRadius: 8, fontSize: '0.8rem',
                     background: '#f8fafc', border: '1px solid #e2e8f0', color: '#4f46e5' }}>
        make api
      </code>
    </motion.div>
  )
}

/* ── Result card ──────────────────────────────────────────────────────────── */
function ResultCard({ prediction, classification, lastFields }) {
  const isLate   = classification.is_late
  const color    = isLate ? '#dc2626' : '#15803d'
  const borderC  = isLate ? '#fecaca'  : '#bbf7d0'
  const topColor = isLate ? '#ef4444'  : '#22c55e'
  const badgeBg  = isLate ? '#fef2f2'  : '#f0fdf4'
  const tip      = isLate
    ? (LATE_TIPS[lastFields?.shipping_mode] || 'Consider upgrading the shipping mode.')
    : 'This order is on track for on-time delivery. No action required.'

  return (
    <motion.div key="result" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ duration: 0.45, ease: [0.34, 1.56, 0.64, 1] }}
      className="card"
      style={{ border: `1px solid ${borderC}`, borderTop: `4px solid ${topColor}`,
               padding: '1.5rem 1.4rem 1.6rem', textAlign: 'center' }}>

      <div className="section-label" style={{ justifyContent: 'center' }}>
        Delivery Risk Assessment
      </div>

      {/* Primary: classification probability gauge */}
      <div style={{ margin: '0.4rem 0 0.8rem' }}>
        <RiskGauge probability={classification.probability} isLate={isLate} />
      </div>

      {/* Verdict badge */}
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.35, duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 7, marginBottom: '1rem',
          background: badgeBg, border: `1.5px solid ${borderC}`,
          borderRadius: 100, padding: '0.45rem 1.4rem',
          fontSize: '1rem', fontWeight: 800, color, letterSpacing: '0.03em',
        }}>
        {isLate ? (
          <>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 strokeWidth="2.5" strokeLinecap="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            LATE DELIVERY
          </>
        ) : (
          <>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 strokeWidth="2.5" strokeLinecap="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            ON TIME
          </>
        )}
      </motion.div>

      {/* Secondary: regression model row */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}>
        <RegressionRow prediction={prediction} />
      </motion.div>

      {/* Tip */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.65 }}
        style={{
          background: '#f8fafc', border: '1px solid #e2e8f0',
          borderLeft: '3px solid #6366f1', borderRadius: '0 8px 8px 0',
          padding: '0.7rem 0.9rem', fontSize: '0.76rem', color: '#475569',
          lineHeight: 1.55, textAlign: 'left',
        }}>
        <span style={{ color: '#4f46e5', fontWeight: 700 }}>Tip: </span>{tip}
      </motion.div>
    </motion.div>
  )
}

/* ── Main export ──────────────────────────────────────────────────────────── */
export default function ResultPanel({ prediction, classification, loading, error, lastFields }) {
  const ready = prediction && classification
  return (
    <AnimatePresence mode="wait">
      {loading
        ? <LoadingState    key="loading" />
        : ready
        ? <ResultCard      key="result"  prediction={prediction} classification={classification} lastFields={lastFields} />
        : error
        ? <ErrorState      key="error"   message={error} />
        : <Placeholder     key="placeholder" />}
    </AnimatePresence>
  )
}
