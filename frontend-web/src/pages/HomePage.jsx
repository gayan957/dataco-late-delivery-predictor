const FACTS = [
  { value: '5',   label: 'Global markets' },
  { value: '164', label: 'Destination countries' },
  { value: '11',  label: 'Product departments' },
  { value: '4',   label: 'Shipping service levels' },
]

const SERVICES = [
  {
    title: 'Order fulfilment',
    text: 'End-to-end processing of customer orders, from payment and picking to packing and dispatch, for consumer, corporate and home-office customers.',
    icon: (
      <path d="M3 7l9-4 9 4-9 4-9-4zm0 0v10l9 4 9-4V7M12 11v10" />
    ),
  },
  {
    title: 'Shipping & delivery',
    text: 'Four service levels – Same Day, First Class, Second Class and Standard Class – connecting customers in Africa, Europe, LATAM, Pacific Asia and USCA.',
    icon: (
      <path d="M1 6h13v10H1zM14 10h4l3 3v3h-7M5.5 19a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM17.5 19a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
    ),
  },
  {
    title: 'Warehousing & distribution',
    text: 'A network of warehouses and distribution points that stock eleven product departments, including fan shop, apparel, golf, footwear and outdoor goods.',
    icon: (
      <path d="M3 21V9l9-5 9 5v12M7 21v-7h10v7M7 17h10" />
    ),
  },
  {
    title: 'Supply-chain analytics',
    text: 'Data-driven insight into orders, shipping performance and delivery risk, helping teams anticipate late deliveries and keep customer promises.',
    icon: (
      <path d="M4 20V10M10 20V4M16 20v-6M22 20H2" />
    ),
  },
]

function ServiceIcon({ children }) {
  return (
    <span className="service-icon" aria-hidden>
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        {children}
      </svg>
    </span>
  )
}

export default function HomePage() {
  return (
    <div className="home">
      {/* Hero */}
      <section className="org-hero" style={{ backgroundImage: 'url(/logistics-hero.jpg)' }}>
        <div className="org-hero-overlay" />
        <div className="org-container org-hero-content">
          <p className="org-eyebrow org-eyebrow-light">DataCo Global</p>
          <h1 className="org-hero-title">Connecting products to customers across <span className="accent">five continents</span></h1>
          <p className="org-hero-text">
            A global supply-chain company that sources, stores and delivers everyday products to consumers and
            businesses around the world.
          </p>
        </div>
      </section>

      {/* Background */}
      <section className="org-section org-section-tint">
        <div className="org-container org-about">
          <div>
            <p className="org-eyebrow">Background</p>
            <h2 className="org-title">Who we are</h2>
            <p className="org-text">
              DataCo Global is a multinational retail supply-chain organisation. It sells products across eleven
              departments – from sporting goods, apparel and footwear to technology, books and pet supplies – and
              ships them to customers in 164 countries.
            </p>
            <p className="org-text">
              Every order passes through a connected network of suppliers, warehouses and carriers. With customers
              choosing between four delivery service levels, keeping each delivery promise is central to how the
              organisation operates and how it measures success.
            </p>
          </div>
          <dl className="org-facts">
            {FACTS.map(f => (
              <div key={f.label} className="org-fact">
                <dt>{f.label}</dt>
                <dd>{f.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Mission & vision */}
      <section className="org-section">
        <div className="org-container">
          <div className="org-mv">
            <article className="org-mv-card">
              <p className="org-eyebrow">Our mission</p>
              <h2 className="org-mv-title">Deliver the right product, on time, every time.</h2>
              <p className="org-text">
                To provide customers with a dependable shopping and delivery experience by running an efficient,
                transparent supply chain – and by using data to anticipate problems before they reach the customer.
              </p>
            </article>
            <article className="org-mv-card">
              <p className="org-eyebrow">Our vision</p>
              <h2 className="org-mv-title">A supply chain customers can trust.</h2>
              <p className="org-text">
                To become a leading data-driven logistics organisation, where every delivery estimate is realistic,
                every delay is foreseen, and every customer knows exactly when their order will arrive.
              </p>
            </article>
          </div>
        </div>
      </section>

      {/* Services */}
      <section className="org-section org-section-alt">
        <div className="org-container">
          <div className="org-section-head">
            <p className="org-eyebrow">What we do</p>
            <h2 className="org-title">Main services</h2>
          </div>
          <div className="org-services">
            {SERVICES.map(s => (
              <article key={s.title} className="org-service">
                <ServiceIcon>{s.icon}</ServiceIcon>
                <h3 className="org-service-title">{s.title}</h3>
                <p className="org-service-text">{s.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
