import { motion } from 'framer-motion'
import { SHIPPING_INFO } from '../data'

const CLF_METRICS = [
  { label: 'ROC-AUC',   value: '0.773', sub: 'Area under ROC curve',  color: '#15803d', bg: '#f0fdf4', bd: '#bbf7d0' },
  { label: 'Precision', value: '89.4%', sub: 'Of predicted-late, correct', color: '#0891b2', bg: '#ecfeff', bd: '#a5f3fc' },
  { label: 'Recall',    value: '59.2%', sub: 'Late orders caught',    color: '#d97706', bg: '#fffbeb', bd: '#fde68a' },
  { label: 'F1 Score',  value: '0.712', sub: 'Precision × recall',   color: '#7c3aed', bg: '#f5f3ff', bd: '#ddd6fe' },
]

const REG_METRICS = [
  { label: 'MAE',          value: '0.96d',  sub: 'Mean absolute error',  color: '#4f46e5', bg: '#eef2ff', bd: '#c7d2fe' },
  { label: 'R²',           value: '0.39',   sub: 'Variance explained',   color: '#0891b2', bg: '#ecfeff', bd: '#a5f3fc' },
  { label: 'Within 1 day', value: '52.3%',  sub: 'Accurate to ±1 day',  color: '#15803d', bg: '#f0fdf4', bd: '#bbf7d0' },
  { label: 'Dataset',      value: '180K',   sub: 'Orders for training',  color: '#7c3aed', bg: '#f5f3ff', bd: '#ddd6fe' },
]

export default function ModelInfo() {
  return (
    <div style={{ marginTop: '2rem' }}>
      {/* Classification metrics */}
      <div className="section-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
        </svg>
        Classifier Performance
        <span style={{ fontWeight: 500, textTransform: 'none', letterSpacing: 0, color: '#94a3b8', fontSize: '0.7rem' }}>
          &nbsp;— DecisionTree · threshold 0.65 · test set
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.85rem', marginBottom: '1.75rem' }}>
        {CLF_METRICS.map((m, i) => (
          <motion.div key={m.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.4 }} className="card"
            style={{ padding: '1.1rem 0.9rem', textAlign: 'center', borderTop: `3px solid ${m.color}` }}>
            <div style={{ fontSize: '0.6rem', fontWeight: 800, color: '#94a3b8',
                          textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>{m.label}</div>
            <div style={{ fontSize: '1.65rem', fontWeight: 900, color: m.color, lineHeight: 1,
                          background: m.bg, borderRadius: 10, padding: '0.3rem 0' }}>{m.value}</div>
            <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginTop: 6 }}>{m.sub}</div>
          </motion.div>
        ))}
      </div>

      {/* Regression metrics */}
      <div className="section-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
        </svg>
        Regression Performance
        <span style={{ fontWeight: 500, textTransform: 'none', letterSpacing: 0, color: '#94a3b8', fontSize: '0.7rem' }}>
          &nbsp;— DecisionTree · predicts delivery days · test set
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.85rem', marginBottom: '1.75rem' }}>
        {REG_METRICS.map((m, i) => (
          <motion.div key={m.label} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.4 }} className="card"
            style={{ padding: '1.1rem 0.9rem', textAlign: 'center', borderTop: `3px solid ${m.color}` }}>
            <div style={{ fontSize: '0.6rem', fontWeight: 800, color: '#94a3b8',
                          textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>{m.label}</div>
            <div style={{ fontSize: '1.65rem', fontWeight: 900, color: m.color, lineHeight: 1,
                          background: m.bg, borderRadius: 10, padding: '0.3rem 0' }}>{m.value}</div>
            <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginTop: 6 }}>{m.sub}</div>
          </motion.div>
        ))}
      </div>

      {/* Shipping schedule reference */}
      <div className="section-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <rect x="1" y="3" width="15" height="13" rx="2"/><path d="M16 8h5l3 3v5h-8V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
        </svg>
        Shipping Schedule Reference
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.85rem' }}>
        {Object.entries(SHIPPING_INFO).map(([mode, info], i) => (
          <motion.div
            key={mode}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.4 }}
            className="card"
            style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: 6 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                width: 34, height: 34, borderRadius: 10, background: '#f8fafc',
                border: '1px solid #e2e8f0', display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: '1.1rem', flexShrink: 0,
              }}>{info.icon}</span>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0f172a' }}>{mode}</span>
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 900, color: info.color }}>
              {info.days} day{info.days !== 1 ? 's' : ''}
            </div>
            <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>{info.desc}</div>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '1.5rem', paddingTop: '1.1rem',
        borderTop: '1px solid #e2e8f0',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        fontSize: '0.7rem', color: '#94a3b8',
      }}>
        <span>IT3051 · Fundamentals of Data Mining · Group Mini-Project</span>
        <span>DecisionTree (depth=3, min_samples_leaf=50) · scikit-learn · DataCo Supply Chain</span>
      </div>
    </div>
  )
}
