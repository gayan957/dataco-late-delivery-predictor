import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

export const NAV_ITEMS = [
  { path: '/',        label: 'Home',                icon: '🏠' },
  { path: '/eda',     label: 'EDA',                 icon: '📊' },
  { path: '/predict', label: 'Delivery Prediction', icon: '🚚' },
]

function StatusDot({ apiStatus }) {
  if (apiStatus === null) return null
  const color = apiStatus ? '#22c55e' : '#ef4444'
  return (
    <div
      title={apiStatus ? 'API connected' : 'API offline — run: make api'}
      style={{
        display: 'flex', alignItems: 'center', gap: 6,
        background: apiStatus ? '#f0fdf4' : '#fef2f2',
        border: `1px solid ${apiStatus ? '#bbf7d0' : '#fecaca'}`,
        borderRadius: 20, padding: '0.3rem 0.75rem',
        fontSize: '0.68rem', fontWeight: 700,
        color: apiStatus ? '#15803d' : '#b91c1c', whiteSpace: 'nowrap',
      }}
    >
      <span style={{
        width: 7, height: 7, borderRadius: '50%', background: color,
        boxShadow: `0 0 6px ${color}`,
      }} />
      {apiStatus ? 'API Online' : 'API Offline'}
    </div>
  )
}

export default function NavBar({ route, navigate, apiStatus }) {
  const [open, setOpen] = useState(false)

  const go = (path) => {
    setOpen(false)
    navigate(path)
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Brand */}
        <button className="nav-brand" onClick={() => go('/')} aria-label="Go to home page">
          <span className="nav-logo">📦</span>
          <span>
            <span className="nav-title">DataCo Predictor</span>
            <span className="nav-subtitle">Late delivery risk · IT3051</span>
          </span>
        </button>

        {/* Desktop links */}
        <nav className="nav-links" aria-label="Main navigation">
          {NAV_ITEMS.map(item => {
            const active = route === item.path
            return (
              <button
                key={item.path}
                onClick={() => go(item.path)}
                className={`nav-link ${active ? 'nav-link-active' : ''}`}
                aria-current={active ? 'page' : undefined}
              >
                {active && (
                  <motion.span
                    layoutId="nav-pill"
                    className="nav-pill"
                    transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                  />
                )}
                <span style={{ position: 'relative' }}>{item.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="nav-right">
          <StatusDot apiStatus={apiStatus} />
          <button
            className="nav-burger"
            onClick={() => setOpen(o => !o)}
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              {open
                ? <><line x1="6" y1="6" x2="18" y2="18" /><line x1="18" y1="6" x2="6" y2="18" /></>
                : <><line x1="4" y1="7" x2="20" y2="7" /><line x1="4" y1="12" x2="20" y2="12" /><line x1="4" y1="17" x2="20" y2="17" /></>}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {open && (
          <motion.nav
            className="nav-mobile"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            aria-label="Mobile navigation"
          >
            {NAV_ITEMS.map(item => (
              <button
                key={item.path}
                onClick={() => go(item.path)}
                className={`nav-mobile-link ${route === item.path ? 'nav-mobile-link-active' : ''}`}
              >
                <span>{item.icon}</span> {item.label}
              </button>
            ))}
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}
