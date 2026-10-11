import { useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

export const NAV_ITEMS = [
  { path: '/',    label: 'Home' },
  { path: '/eda', label: 'EDA' },
  {
    label: 'Delivery Prediction',
    children: [
      { path: '/predict',  label: 'Logistics', desc: 'Full delivery-risk analysis for operations teams' },
      { path: '/customer', label: 'Customer',  desc: 'Simple delivery-time estimate for shoppers' },
    ],
  },
]

// Every page as a flat list – used for the footer and the document title.
export const PAGE_LINKS = NAV_ITEMS.flatMap(item =>
  item.children
    ? item.children.map(c => ({ path: c.path, label: `${c.label} Prediction` }))
    : [item]
)

function StatusDot({ apiStatus }) {
  if (apiStatus === null) return null
  const color = apiStatus ? '#22c55e' : '#ef4444'
  return (
    <div
      title={apiStatus ? 'API connected' : 'API offline — run: make api'}
      style={{
        display: 'flex', alignItems: 'center', gap: 6,
        background: apiStatus ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
        border: `1px solid ${apiStatus ? 'rgba(34,197,94,0.35)' : 'rgba(239,68,68,0.35)'}`,
        borderRadius: 20, padding: '0.3rem 0.75rem',
        fontSize: '0.68rem', fontWeight: 700,
        color: apiStatus ? '#86efac' : '#fca5a5', whiteSpace: 'nowrap',
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

function ActivePill() {
  return (
    <motion.span
      layoutId="nav-pill"
      className="nav-pill"
      transition={{ type: 'spring', stiffness: 420, damping: 34 }}
    />
  )
}

function Dropdown({ item, route, go }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const active = item.children.some(c => c.path === route)

  useEffect(() => {
    if (!open) return
    const onDown = (e) => { if (!ref.current?.contains(e.target)) setOpen(false) }
    const onKey  = (e) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('mousedown', onDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div
      ref={ref}
      className="nav-dropdown"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        className={`nav-link ${active ? 'nav-link-active' : ''}`}
        onClick={() => setOpen(o => !o)}
        aria-haspopup="menu"
        aria-expanded={open}
      >
        {active && <ActivePill />}
        <span style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          {item.label}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6"
               strokeLinecap="round" strokeLinejoin="round"
               style={{ transition: 'transform 0.2s', transform: open ? 'rotate(180deg)' : 'none' }}>
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </span>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="nav-menu"
            role="menu"
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.16 }}
          >
            {item.children.map(c => (
              <button
                key={c.path}
                role="menuitem"
                className={`nav-menu-item ${route === c.path ? 'nav-menu-item-active' : ''}`}
                onClick={() => { setOpen(false); go(c.path) }}
              >
                <span className="nav-menu-label">{c.label}</span>
                <span className="nav-menu-desc">{c.desc}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
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
        <button className="nav-brand" onClick={() => go('/')} aria-label="DataCo Global – home">
          <span className="nav-wordmark">DataCo <em>Global</em></span>
        </button>

        {/* Desktop links */}
        <nav className="nav-links" aria-label="Main navigation">
          {NAV_ITEMS.map(item => {
            if (item.children) return <Dropdown key={item.label} item={item} route={route} go={go} />
            const active = route === item.path
            return (
              <button
                key={item.path}
                onClick={() => go(item.path)}
                className={`nav-link ${active ? 'nav-link-active' : ''}`}
                aria-current={active ? 'page' : undefined}
              >
                {active && <ActivePill />}
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
            {NAV_ITEMS.map(item => item.children ? (
              <div key={item.label}>
                <div className="nav-mobile-group">{item.label}</div>
                {item.children.map(c => (
                  <button
                    key={c.path}
                    onClick={() => go(c.path)}
                    className={`nav-mobile-link nav-mobile-sublink ${route === c.path ? 'nav-mobile-link-active' : ''}`}
                  >
                    {c.label}
                  </button>
                ))}
              </div>
            ) : (
              <button
                key={item.path}
                onClick={() => go(item.path)}
                className={`nav-mobile-link ${route === item.path ? 'nav-mobile-link-active' : ''}`}
              >
                {item.label}
              </button>
            ))}
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}
