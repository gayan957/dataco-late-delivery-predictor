import { motion } from 'framer-motion'
import { SHIPPING_INFO } from '../data'

// Hidden test-set results (notebooks 09 / C09). Baseline = predict from shipping mode alone.
const CLF_ROWS = [
  { metric: 'ROC-AUC',   model: '0.773', base: '0.743', desc: 'How well late and on-time orders are separated' },
  { metric: 'Accuracy',  model: '72.4%', base: '69.9%', desc: 'Share of all orders classified correctly' },
  { metric: 'Precision', model: '89.4%', base: '88.8%', desc: 'Orders flagged as late that really were late' },
  { metric: 'Recall',    model: '59.2%', base: '54.9%', desc: 'Late orders that the model caught' },
  { metric: 'F1 score',  model: '0.712', base: '0.678', desc: 'Balance of precision and recall' },
]

const REG_ROWS = [
  { metric: 'MAE',          model: '0.94 days', base: '0.96 days', desc: 'Average error in shipping days' },
  { metric: 'RMSE',         model: '1.25 days', base: '1.25 days', desc: 'Error that penalises large misses' },
  { metric: 'R²',           model: '0.402',     base: '0.397',     desc: 'Share of variation in shipping time explained' },
  { metric: 'Within ±1 day', model: '53.6%',    base: '53.6%',     desc: 'Orders predicted to within one day' },
  { metric: 'Bias',         model: '+0.005 days', base: '+0.007 days', desc: 'Average over- or under-estimate' },
]

// Training-set mean real shipping days and test-set late rate per mode.
const MODE_STATS = {
  'Same Day':       { actual: '0.5 days', late: '45.0%' },
  'First Class':    { actual: '2.0 days', late: '100.0%' },
  'Second Class':   { actual: '4.0 days', late: '79.8%' },
  'Standard Class': { actual: '4.0 days', late: '40.1%' },
}

function MetricTable({ title, subtitle, rows }) {
  return (
    <div className="card perf-card">
      <div className="perf-head">
        <h3 className="perf-title">{title}</h3>
        <p className="perf-sub">{subtitle}</p>
      </div>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th className="num">Final model</th>
              <th className="num">Baseline</th>
              <th className="hide-sm">Meaning</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.metric}>
                <td className="metric">{r.metric}</td>
                <td className="num strong">{r.model}</td>
                <td className="num muted">{r.base}</td>
                <td className="hide-sm muted">{r.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function ModelInfo() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      style={{ marginTop: '2rem' }}
    >
      <div className="perf-section-head">
        <h2 className="perf-section-title">Model performance</h2>
        <p className="perf-sub">
          Results on the hidden test set of unseen orders. The baseline predicts from shipping mode alone.
        </p>
      </div>

      <div className="perf-grid">
        <MetricTable
          title="Late-delivery classifier"
          subtitle="Decision Tree · alert threshold 0.65 · 34,534 test rows"
          rows={CLF_ROWS}
        />
        <MetricTable
          title="Shipping-days regression"
          subtitle="Decision Tree (depth 3) · 34,667 test rows"
          rows={REG_ROWS}
        />
      </div>

      <div className="card perf-card" style={{ marginTop: '1.25rem' }}>
        <div className="perf-head">
          <h3 className="perf-title">Shipping schedule reference</h3>
          <p className="perf-sub">Promised delivery window for each mode, compared with what actually happens.</p>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Shipping mode</th>
                <th className="num">Scheduled</th>
                <th className="num">Average actual</th>
                <th className="num">Late rate</th>
                <th className="hide-sm">Service</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(SHIPPING_INFO).map(([mode, info]) => (
                <tr key={mode}>
                  <td className="metric">{mode}</td>
                  <td className="num">{info.days} {info.days === 1 ? 'day' : 'days'}</td>
                  <td className="num">{MODE_STATS[mode]?.actual}</td>
                  <td className="num strong">{MODE_STATS[mode]?.late}</td>
                  <td className="hide-sm muted">{info.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </motion.section>
  )
}
