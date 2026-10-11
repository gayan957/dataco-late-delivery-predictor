import { useCallback, useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

const EASE = [0.16, 1, 0.3, 1]

const SECTIONS = [
  { id: 'target',   label: 'Target',              icon: '🎯', intro: 'What we predict: the real number of shipping days (regression) and whether the order is late (classification).' },
  { id: 'drivers',  label: 'Drivers of delay',    icon: '🚚', intro: 'Which order-time factors are related to shipping time and late delivery.' },
  { id: 'time',     label: 'Time patterns',       icon: '🕒', intro: 'Does the day, hour, month or year of the order change shipping behaviour?' },
  { id: 'quality',  label: 'Data quality',        icon: '🧹', intro: 'Outliers, correlations and consistency checks that shaped the cleaning decisions.' },
  { id: 'features', label: 'Feature engineering', icon: '🧩', intro: 'How categorical features were encoded and which features carry real signal.' },
  { id: 'models',   label: 'Model results',       icon: '🏆', intro: 'How the five tuned algorithms compared, and how the final models performed on hidden test data.' },
]

const REG = 'Regression'
const CLF = 'Classification'

const FIGURES = [
  // ── Target
  { section: 'target', task: REG, src: 'm2/01_target_distribution.png',
    title: 'Distribution of real shipping days',
    text: 'Shipping time takes whole values from 0 to 6 days (mean 3.50, std 1.63). Two days is the most common value (31.4 %), and days 3–6 each hold about 16 %.',
    insight: 'Skewness is only 0.09 – no long tail, so no log transform is needed.' },
  { section: 'target', task: CLF, src: 'clf_m2/01_class_balance.png',
    title: 'Late vs on-time orders',
    text: 'After cleaning, about 57 % of training order items are late and 43 % arrive on time.',
    insight: 'Only mild imbalance, so ROC-AUC is used as the main score, with recall as the business priority.' },

  // ── Drivers
  { section: 'drivers', task: REG, src: 'm2/02_days_by_shipping_mode.png',
    title: 'Shipping days by shipping mode',
    text: 'Same Day averages 0.49 days and First Class is always exactly 2 days. Second and Standard Class both average about 4 days, spread evenly from 2 to 6.',
    insight: 'Shipping mode alone explains 38.9 % of the variation (η² = 0.389), far more than any other feature.' },
  { section: 'drivers', task: CLF, src: 'clf_m2/02_late_rate_by_mode.png',
    title: 'Late rate by shipping mode',
    text: 'First Class is late 100 % of the time (2 days against a 1-day promise). Second Class is late about 80 %, Same Day about 48 % and Standard Class about 40 %.',
    insight: 'The fastest premium options are the most likely to break their promise.' },
  { section: 'drivers', task: REG, src: 'm2/03_days_by_market.png',
    title: 'Shipping days by market',
    text: 'All five markets (USCA, Europe, LATAM, Pacific Asia, Africa) average almost exactly 3.5 days.',
    insight: 'Destination region explains almost nothing on its own (η² = 0.0001) – still a useful finding.' },
  { section: 'drivers', task: CLF, src: 'clf_m2/03_late_rate_by_market.png',
    title: 'Late rate by market',
    text: 'The late rate is about 57 % in every market.',
    insight: 'Where an order goes matters much less than how it is shipped.' },

  // ── Time
  { section: 'time', task: CLF, src: 'clf_m2/07_late_by_hour.png',
    title: 'Late rate by order hour',
    text: 'Orders placed before noon are late about 54 % of the time; orders placed in the afternoon about 60 %.',
    insight: 'The decision tree uses this: Same Day orders before 11:30 ship in 0 days, later ones in 1 day.' },
  { section: 'time', task: REG, src: 'm2/07_days_by_hour.png',
    title: 'Shipping days by order hour',
    text: 'Averaged over all modes, shipping time is flat across the day at about 3.5 days.',
    insight: 'The hour effect only appears inside Same Day orders, which is why a tree (not a linear model) captures it.' },
  { section: 'time', task: REG, src: 'm2/06_days_by_weekday.png',
    title: 'Shipping days by weekday',
    text: 'Orders placed on any day of the week take about the same time to ship, weekends included.',
    insight: 'Weekday and is_weekend were kept as features but carry very little signal (η² ≈ 0).' },
  { section: 'time', task: CLF, src: 'clf_m2/06_late_by_weekday.png',
    title: 'Late rate by weekday',
    text: 'The late rate stays close to 57 % from Monday to Sunday.',
    insight: 'No weekend effect on late delivery.' },
  { section: 'time', task: REG, src: 'm2/09_days_by_month.png',
    title: 'Shipping days by month',
    text: 'Average shipping time barely changes from January to December.',
    insight: 'Very weak seasonality (η² = 0.0005).' },
  { section: 'time', task: REG, src: 'm2/08_days_over_time.png',
    title: 'Shipping days over time (2015–2018)',
    text: 'The monthly average stays between 3.40 and 3.63 days across 37 months.',
    insight: 'No drift over time, so a grouped random train/test split is acceptable.' },
  { section: 'time', task: CLF, src: 'clf_m2/08_late_over_time.png',
    title: 'Late rate over time',
    text: 'The monthly late rate is stable throughout 2015–2018.',
    insight: 'Behaviour is consistent – the model does not need a time-based split.' },

  // ── Quality
  { section: 'quality', task: REG, src: 'm2/04_correlation_heatmap.png',
    title: 'Correlation of numeric columns',
    text: 'All price, discount, profit, quantity and location columns have a correlation below 0.01 with shipping days. Sales and Sales per customer are almost identical (r = 0.99).',
    insight: 'Financial columns do not predict shipping time, so they were left out of the final features.' },
  { section: 'quality', task: REG, src: 'm2/05_boxplot_financial.png',
    title: 'Outliers in financial columns',
    text: 'Benefit per order has 10.4 % outliers and 18.7 % negative values (down to −4,274.98).',
    insight: 'Kept: the money columns agree with each other, so these are genuine losses, not errors.' },

  // ── Features
  { section: 'features', task: REG, src: 'm3/01_long_tail.png',
    title: 'Long tail of Order Country',
    text: 'There are 161 destination countries. The top 20 cover 74 % of rows and the top 50 cover 93 %; most countries have very few orders.',
    insight: 'One-hot encoding would create many near-empty columns, so target encoding was considered.' },
  { section: 'features', task: REG, src: 'm3/02_encoding_comparison.png',
    title: 'Encoding strategies compared',
    text: 'Dropping, one-hot, one-hot with rare grouping and target encoding were compared with Ridge and a gradient-boosted tree on the same grouped folds.',
    insight: 'Target encoding won (MAE 0.9836) with the lowest fold-to-fold noise.' },
  { section: 'features', task: REG, src: 'm3/03_drop_column_importance.png',
    title: 'Drop-column importance',
    text: 'Each feature was removed in turn and the model retrained. Removing Shipping Mode raises the error by 0.44 days; the five date features together add 0.005.',
    insight: 'Shipping mode carries almost all the signal; the other features are within noise.' },
  { section: 'features', task: REG, src: 'm4/03_scaling_comparison.png',
    title: 'Effect of feature scaling',
    text: 'Scaling makes no difference to Ridge, but KNN improves from MAE 1.30 (no scaling) to 1.05 (MinMax).',
    insight: 'MinMax was used for linear and KNN models; tree models need no scaling.' },

  // ── Models
  { section: 'models', task: REG, src: 'final/01_model_comparison.png',
    title: 'Regression models compared',
    text: 'Decision Tree (0.962), Random Forest (0.965) and XGBoost (0.969) are statistically tied and are the only models that beat the shipping-mode baseline (0.987).',
    insight: 'The simplest of the tied models – the Decision Tree – was selected.' },
  { section: 'models', task: REG, src: 'final/03_predicted_vs_actual.png',
    title: 'Predicted vs actual days (test set)',
    text: 'Same Day and First Class orders are predicted exactly. For 3–6 day orders the model predicts about 4 days.',
    insight: 'Test MAE 0.937 days, R² 0.402 – slightly better than cross-validation, so no over-fitting.' },
  { section: 'models', task: REG, src: 'final/02_test_errors.png',
    title: 'Test-set prediction errors',
    text: 'Errors cluster at whole days and never exceed ±2 days; the average error (bias) is almost exactly zero.',
    insight: 'The model does not systematically over- or under-promise.' },
  { section: 'models', task: REG, src: 'final/04_feature_importance.png',
    title: 'What drives the regression model',
    text: 'Shuffling Shipping Mode raises the error by about 0.6 days; order hour is a distant second.',
    insight: 'Matches the EDA: mode first, then the time the order was placed.' },
  { section: 'models', task: CLF, src: 'clf_final/01_model_comparison.png',
    title: 'Classifiers compared (ROC-AUC)',
    text: 'Decision Tree (0.776), XGBoost (0.774) and Random Forest (0.773) lead; all models beat the shipping-mode baseline (0.741).',
    insight: 'The Decision Tree classifier was selected (tie with XGBoost, simpler model).' },
  { section: 'models', task: CLF, src: 'clf_final/02_threshold_tradeoff.png',
    title: 'Choosing the alert threshold',
    text: 'Precision, recall and false-alarm rate at each threshold, measured on out-of-fold training predictions.',
    insight: 'Threshold 0.65 keeps precision at 0.89 with a 9 % false-alarm rate.' },
  { section: 'models', task: CLF, src: 'clf_final/03_confusion_matrix.png',
    title: 'Confusion matrix (test set)',
    text: 'Results on 34,534 unseen order items at threshold 0.65.',
    insight: 'Accuracy 0.724 · precision 0.894 · recall 0.592 · F1 0.712.' },
  { section: 'models', task: CLF, src: 'clf_final/04_roc_curve.png',
    title: 'ROC curve (test set)',
    text: 'The curve bows well above the diagonal (random guessing).',
    insight: 'Test ROC-AUC 0.773 vs 0.743 for the shipping-mode baseline.' },
]

const FUNNEL = [
  { value: '180,519', label: 'Raw order items', sub: '53 columns · 65,752 orders' },
  { value: '−7,754',  label: 'Cancelled / fraud removed', sub: 'never shipped' },
  { value: '172,765', label: 'Clean rows', sub: '28 columns · 0 missing' },
  { value: '138,098', label: 'Training set', sub: '50,318 orders' },
  { value: '34,667',  label: 'Hidden test set', sub: '12,579 orders · 0 overlap' },
]

const LEAKS = [
  { col: 'Late_delivery_risk',          why: '= real days > scheduled days (97.5 % of rows)' },
  { col: 'Delivery Status',             why: 'Text version of the same comparison' },
  { col: 'shipping date (DateOrders)',  why: 'Order date + real shipping days (97.4 %)' },
  { col: 'Order Status',                why: 'Recorded after fulfilment' },
]

function FigureCard({ fig, onOpen, index }) {
  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.97 }}
      transition={{ duration: 0.4, delay: Math.min(index, 6) * 0.04, ease: EASE }}
      className="card fig-card"
    >
      <button className="fig-image-btn" onClick={onOpen} aria-label={`Enlarge chart: ${fig.title}`}>
        <img src={`/figures/${fig.src}`} alt={fig.title} loading="lazy" />
        <span className="fig-zoom">⤢ Enlarge</span>
      </button>
      <div className="fig-body">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <span className={`task-tag ${fig.task === REG ? 'task-reg' : 'task-clf'}`}>{fig.task}</span>
        </div>
        <h3 className="fig-title">{fig.title}</h3>
        <p className="fig-text">{fig.text}</p>
        <div className="fig-insight"><span>💡</span><span>{fig.insight}</span></div>
      </div>
    </motion.article>
  )
}

function Lightbox({ figures, index, onClose, onMove }) {
  const fig = figures[index]

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowRight') onMove(1)
      if (e.key === 'ArrowLeft') onMove(-1)
    }
    window.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [onClose, onMove])

  return (
    <motion.div
      className="lightbox"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={fig.title}
    >
      <motion.div
        className="lightbox-panel"
        initial={{ scale: 0.95, y: 10 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95 }}
        transition={{ duration: 0.25, ease: EASE }}
        onClick={e => e.stopPropagation()}
      >
        <button className="lightbox-close" onClick={onClose} aria-label="Close">✕</button>
        <img src={`/figures/${fig.src}`} alt={fig.title} />
        <div className="lightbox-caption">
          <span className={`task-tag ${fig.task === REG ? 'task-reg' : 'task-clf'}`}>{fig.task}</span>
          <h3 className="fig-title" style={{ marginTop: 8 }}>{fig.title}</h3>
          <p className="fig-text">{fig.text}</p>
          <div className="fig-insight"><span>💡</span><span>{fig.insight}</span></div>
          <div className="lightbox-nav">
            <button onClick={() => onMove(-1)} aria-label="Previous chart">← Previous</button>
            <span>{index + 1} / {figures.length}</span>
            <button onClick={() => onMove(1)} aria-label="Next chart">Next →</button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default function EdaPage({ navigate }) {
  const [section, setSection] = useState('all')
  const [task, setTask]       = useState('all')
  const [open, setOpen]       = useState(null)

  const visible = useMemo(() => FIGURES.filter(f =>
    (section === 'all' || f.section === section) && (task === 'all' || f.task === task)
  ), [section, task])

  const move = useCallback((d) => {
    setOpen(i => (i + d + visible.length) % visible.length)
  }, [visible.length])
  const close = useCallback(() => setOpen(null), [])

  const groups = SECTIONS
    .map(s => ({ ...s, figs: visible.filter(f => f.section === s.id) }))
    .filter(g => g.figs.length)

  return (
    <div className="page-container" style={{ maxWidth: 1300, margin: '0 auto', padding: '2rem 1.5rem 4rem' }}>
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: EASE }}
        className="page-hero eda-hero"
      >
        <div className="eda-hero-circle" />
        <div style={{ position: 'relative', zIndex: 1, maxWidth: 720 }}>
          <div className="hero-pill hero-pill-dark">📊 Exploratory Data Analysis</div>
          <h1 className="eda-hero-title">What drives late deliveries?</h1>
          <p className="eda-hero-sub">
            Charts and findings from the project's EDA notebooks, all computed on the <strong>training set only</strong>, followed by
            the feature-engineering experiments and the final model results. Click any chart to enlarge it.
          </p>
        </div>
      </motion.section>

      {/* Pipeline funnel */}
      <section className="funnel">
        {FUNNEL.map((f, i) => (
          <motion.div
            key={f.label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.07, ease: EASE }}
            className="card funnel-step"
          >
            <div className="funnel-value" style={{ color: f.value.startsWith('−') ? '#dc2626' : '#4338ca' }}>{f.value}</div>
            <div className="funnel-label">{f.label}</div>
            <div className="funnel-sub">{f.sub}</div>
          </motion.div>
        ))}
      </section>

      {/* Leakage panel */}
      <section className="card leak-panel">
        <div>
          <div className="eyebrow" style={{ textAlign: 'left' }}>Leakage control</div>
          <h2 style={{ margin: '0.2rem 0 0.4rem', fontSize: '1.15rem', fontWeight: 800 }}>Columns that would give away the answer</h2>
          <p className="fig-text" style={{ margin: 0 }}>
            The model runs at checkout, so anything recorded after shipping is forbidden. Each column was proven to leak, then removed.
          </p>
        </div>
        <div className="leak-list">
          {LEAKS.map(l => (
            <div key={l.col} className="leak-item">
              <code>{l.col}</code>
              <span>{l.why}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Filters */}
      <div className="eda-filters">
        <div className="filter-row" role="tablist" aria-label="Section">
          <button className={`filter-chip ${section === 'all' ? 'filter-chip-active' : ''}`} onClick={() => setSection('all')}>All sections</button>
          {SECTIONS.map(s => (
            <button
              key={s.id}
              className={`filter-chip ${section === s.id ? 'filter-chip-active' : ''}`}
              onClick={() => setSection(s.id)}
            >
              <span>{s.icon}</span> {s.label}
            </button>
          ))}
        </div>
        <div className="segmented" role="tablist" aria-label="Task">
          {['all', REG, CLF].map(t => (
            <button key={t} className={task === t ? 'segmented-active' : ''} onClick={() => setTask(t)}>
              {t === 'all' ? 'Both tasks' : t}
            </button>
          ))}
        </div>
      </div>

      {/* Sections */}
      {groups.length === 0 && (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
          No charts for this combination – try “Both tasks”.
        </div>
      )}
      {groups.map(g => (
        <section key={g.id} className="eda-section">
          <div className="eda-section-head">
            <span className="eda-section-icon">{g.icon}</span>
            <div>
              <h2 className="eda-section-title">{g.label}</h2>
              <p className="fig-text" style={{ margin: 0 }}>{g.intro}</p>
            </div>
          </div>
          <motion.div layout className="fig-grid">
            <AnimatePresence mode="popLayout">
              {g.figs.map((fig, i) => (
                <FigureCard
                  key={fig.src}
                  fig={fig}
                  index={i}
                  onOpen={() => setOpen(visible.indexOf(fig))}
                />
              ))}
            </AnimatePresence>
          </motion.div>
        </section>
      ))}

      {/* CTA */}
      <section className="card eda-cta">
        <div>
          <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Put the findings to work</h2>
          <p className="fig-text" style={{ margin: '0.3rem 0 0' }}>
            Try different shipping modes and order times and see how the prediction changes.
          </p>
        </div>
        <button className="btn-cta" onClick={() => navigate('/predict')}>Open Delivery Prediction →</button>
      </section>

      <AnimatePresence>
        {open !== null && visible[open] && (
          <Lightbox figures={visible} index={open} onClose={close} onMove={move} />
        )}
      </AnimatePresence>
    </div>
  )
}
