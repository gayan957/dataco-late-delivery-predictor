import { useState, useEffect, useCallback } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import NavBar, { NAV_ITEMS } from './components/NavBar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import EdaPage from './pages/EdaPage'
import PredictionPage from './pages/PredictionPage'
import { checkHealth } from './api'

const PAGES = {
  '/':        HomePage,
  '/eda':     EdaPage,
  '/predict': PredictionPage,
}

// Hash routing (#/eda) keeps the app a static SPA with no router dependency.
function readRoute() {
  const path = window.location.hash.replace(/^#/, '') || '/'
  return PAGES[path] ? path : '/'
}

export default function App() {
  const [route, setRoute]         = useState(readRoute)
  const [apiStatus, setApiStatus] = useState(null)

  useEffect(() => {
    const onHash = () => setRoute(readRoute())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    checkHealth().then(ok => setApiStatus(ok))
  }, [])

  useEffect(() => {
    const item = NAV_ITEMS.find(i => i.path === route)
    document.title = `${item?.label ?? 'Home'} · DataCo Delivery Predictor`
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [route])

  const navigate = useCallback((path) => {
    window.location.hash = path
  }, [])

  const Page = PAGES[route]

  return (
    <div style={{ minHeight: '100vh', background: '#f1f5f9', display: 'flex', flexDirection: 'column' }}>
      <NavBar route={route} navigate={navigate} apiStatus={apiStatus} />
      <main style={{ flex: 1 }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={route}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            <Page navigate={navigate} apiStatus={apiStatus} />
          </motion.div>
        </AnimatePresence>
      </main>
      <Footer navigate={navigate} />
    </div>
  )
}
