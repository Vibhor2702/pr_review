import { Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './components/theme-provider'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { ReviewForm } from './pages/ReviewForm'
import { ReviewResults } from './pages/ReviewResults'
import { Analytics } from './pages/Analytics'
import { Settings } from './pages/Settings'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="pr-review-agent-theme">
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/review" element={<ReviewForm />} />
          <Route path="/review/:id" element={<ReviewResults />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  )
}

export default App