import { PAGE_LINKS } from './NavBar'

// Placeholder contact details (555-01xx numbers and .example domains are reserved for fiction).
const CONTACT = [
  { label: 'Phone',   value: '+1 (555) 014-2260', href: 'tel:+15550142260' },
  { label: 'Email',   value: 'support@dataco-global.example', href: 'mailto:support@dataco-global.example' },
  { label: 'Address', value: '100 Harbour Way, Logistics Park, Suite 400' },
  { label: 'Hours',   value: 'Mon – Fri, 8:00 – 18:00' },
]

export default function Footer({ navigate }) {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner footer-grid">
        <div>
          <div className="nav-wordmark" style={{ fontSize: '1.15rem', marginBottom: 10 }}>DataCo <em>Global</em></div>
          <p className="footer-about">
            A global supply-chain company delivering sporting goods, apparel, technology and everyday products to
            customers in 164 countries across five markets.
          </p>
        </div>

        <div>
          <div className="footer-heading">Pages</div>
          <div className="footer-links">
            {PAGE_LINKS.map(item => (
              <button key={item.path} onClick={() => navigate(item.path)} className="footer-link">
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <div className="footer-heading">Contact</div>
          <dl className="footer-contact">
            {CONTACT.map(c => (
              <div key={c.label}>
                <dt>{c.label}</dt>
                <dd>{c.href ? <a href={c.href}>{c.value}</a> : c.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-bottom-inner">© {new Date().getFullYear()} DataCo Global. All rights reserved.</div>
      </div>
    </footer>
  )
}
