import { PAGE_LINKS } from './NavBar'

export default function Footer({ navigate }) {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div>
          <div className="nav-wordmark" style={{ fontSize: '1.15rem', marginBottom: 8 }}>DataCo <em>Global</em></div>
          <p style={{ margin: 0, maxWidth: 420, lineHeight: 1.6 }}>
            IT3051 Fundamentals of Data Mining · Group Mini-Project 2026.
            Dataset: DataCo Smart Supply Chain (Mendeley Data, DOI 10.17632/8gx2fvg2k6.1).
          </p>
        </div>
        <div className="footer-links">
          {PAGE_LINKS.map(item => (
            <button key={item.path} onClick={() => navigate(item.path)} className="footer-link">
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </footer>
  )
}
