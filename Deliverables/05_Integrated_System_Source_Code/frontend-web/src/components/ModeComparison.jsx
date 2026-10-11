import { motion } from 'framer-motion'
import { SHIPPING_INFO, SCHEDULED_DAYS } from '../data'

const MODE_ORDER = ['Same Day', 'First Class', 'Second Class', 'Standard Class']

export default function ModeComparison({ data, selectedMode }) {
  const map = {}
  data.forEach((r) => { map[r.shipping_mode] = r })

  return (
    <div style={{ marginTop: '1.75rem' }}>
      <div className="section-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
        </svg>
        Shipping Mode Comparison
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.85rem' }}>
        {MODE_ORDER.map((mode, i) => {
          const r      = map[mode]
          if (!r) return null
          const info   = SHIPPING_INFO[mode]
          const isLate = r.is_late
          const isSel  = mode === selectedMode
          const color  = isLate ? '#dc2626' : '#15803d'
          const bgClr  = isLate ? '#fef2f2' : '#f0fdf4'
          const bdClr  = isLate ? '#fecaca' : '#bbf7d0'
          const barClr = isLate ? '#ef4444' : '#22c55e'

          return (
            <motion.div
              key={mode}
              className="mode-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07, duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
              style={{
                background: isSel ? '#eef2ff' : '#ffffff',
                border: isSel ? '1.5px solid #818cf8' : '1px solid #e2e8f0',
                boxShadow: isSel ? '0 0 0 3px rgba(99,102,241,0.12)' : '0 1px 3px rgba(0,0,0,0.06)',
              }}
            >
              {/* Mode icon */}
              <div style={{ fontSize: '1.5rem', marginBottom: 5 }}>{info.icon}</div>

              <div style={{
                fontSize: '0.63rem', fontWeight: 800, color: '#334155',
                textTransform: 'uppercase', letterSpacing: '0.08em', lineHeight: 1.3, marginBottom: 8,
              }}>
                {mode}
                {isSel && (
                  <div style={{
                    color: '#4f46e5', fontSize: '0.57rem', marginTop: 2,
                    background: '#eef2ff', borderRadius: 3, padding: '1px 4px',
                    display: 'inline-block',
                  }}>selected</div>
                )}
              </div>

              {/* Predicted days */}
              <div style={{ fontSize: '1.5rem', fontWeight: 900, color, marginBottom: 2, lineHeight: 1 }}>
                {r.predicted_days.toFixed(1)}d
              </div>

              <div style={{ fontSize: '0.62rem', color: '#94a3b8', marginBottom: 8 }}>
                sched: {SCHEDULED_DAYS[mode]}d
              </div>

              {/* Late/on-time badge */}
              <div style={{
                display: 'inline-block',
                background: bgClr, border: `1px solid ${bdClr}`,
                borderRadius: 6, padding: '2px 9px',
                fontSize: '0.63rem', fontWeight: 700, color,
              }}>
                {isLate ? 'LATE' : 'ON TIME'}
              </div>

              {/* Mini bar */}
              <div style={{
                marginTop: 10, height: 4, borderRadius: 4,
                background: '#f1f5f9', overflow: 'hidden',
              }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(100, (r.predicted_days / 7) * 100)}%` }}
                  transition={{ delay: 0.3 + i * 0.07, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                  style={{ height: '100%', background: barClr, borderRadius: 4 }}
                />
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
