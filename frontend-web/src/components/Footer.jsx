import { NAV_ITEMS } from './NavBar'

export default function Footer({ navigate }) {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <span className="nav-logo" style={{ width: 34, height: 34, fontSize: '1rem' }}>📦</span>
            <span style={{ fontWeight: 800, color: '#fff' }}>DataCo Late Delivery Predictor</span>
          </div>
          <p style={{ margin: 0, maxWidth: 420, lineHeight: 1.6 }}>
            IT3051 Fundamentals of Data Mining · Group Mini-Project 2026.
            Dataset: DataCo Smart Supply Chain (Mendeley Data, DOI 10.17632/8gx2fvg2k6.1).
          </p>
        </div>
        <div className="footer-links">
          {NAV_ITEMS.map(item => (
            <button key={item.path} onClick={() => navigate(item.path)} className="footer-link">
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </footer>
  )
}
