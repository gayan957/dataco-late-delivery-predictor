import { motion } from 'framer-motion'

export default function Header({ apiStatus }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="mb-6"
      style={{
        background: 'linear-gradient(135deg, rgba(99,102,241,0.11) 0%, rgba(139,92,246,0.07) 50%, rgba(6,182,212,0.05) 100%)',
        border: '1px solid rgba(99,102,241,0.18)',
        borderRadius: 20,
        padding: '1.3rem 1.8rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1.2rem',
        position: 'relative',
        overflow: 'hidden',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Ambient glow */}
      <div style={{
        position: 'absolute', top: '-50%', left: '-5%', width: '35%', height: '200%',
        background: 'radial-gradient(ellipse, rgba(99,102,241,0.09) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Icon */}
      <div style={{
        width: 52, height: 52, flexShrink: 0,
        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        borderRadius: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '1.55rem',
        boxShadow: '0 8px 24px rgba(99,102,241,0.45)',
      }}>📦</div>

      {/* Title */}
      <div style={{ flex: 1 }}>
        <h1 style={{
          fontSize: '1.52rem', fontWeight: 900, margin: '0 0 4px',
          lineHeight: 1.1, letterSpacing: '-0.025em',
          background: 'linear-gradient(135deg, #e2e8f0 0%, #a5b4fc 55%, #67e8f9 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}>DataCo Delivery Predictor</h1>
        <p style={{
          fontSize: '0.68rem', color: '#475569', fontWeight: 600,
          letterSpacing: '0.08em', textTransform: 'uppercase', margin: 0,
        }}>IT3051 · Fundamentals of Data Mining · Supply Chain Intelligence</p>
      </div>

      {/* Model badge */}
      <div style={{
        flexShrink: 0,
        background: 'rgba(99,102,241,0.1)',
        border: '1px solid rgba(99,102,241,0.22)',
        borderRadius: 12, padding: '0.6rem 1rem', textAlign: 'right',
      }}>
        <div style={{ fontSize: '0.6rem', color: '#818cf8', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 2 }}>
          Active Model
        </div>
        <div style={{ fontSize: '0.88rem', color: '#e2e8f0', fontWeight: 700, lineHeight: 1.2 }}>
          Decision Tree
        </div>
        <div style={{ fontSize: '0.67rem', color: '#64748b', marginTop: 2 }}>
          MAE&nbsp;0.96d · R²&nbsp;0.39 · 180K rows
        </div>
      </div>

      {/* API dot */}
      {apiStatus !== null && (
        <div
          title={apiStatus ? 'API connected' : 'API offline — run: make api'}
          style={{
            width: 9, height: 9, borderRadius: '50%', flexShrink: 0,
            background: apiStatus ? '#10b981' : '#f43f5e',
            boxShadow: `0 0 8px ${apiStatus ? '#10b981' : '#f43f5e'}88`,
          }}
        />
      )}
    </motion.header>
  )
}
