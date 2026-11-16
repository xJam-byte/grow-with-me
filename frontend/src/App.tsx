import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { HomePage } from './pages/HomePage'
import { HabitsPage } from './pages/HabitsPage'
import { GrowthPage } from './pages/GrowthPage'
import { JournalPage } from './pages/JournalPage'
import { AICoachPage } from './pages/AICoachPage'
import { SettingsPage } from './pages/SettingsPage'
import { KnowledgePage } from './pages/KnowledgePage'
import { SpiritualPage } from './pages/SpiritualPage'
import { useTelegram } from './hooks/useTelegram'
import { useThemeStore } from './stores/useThemeStore'

export const App: React.FC = () => {
  const { ready, expand } = useTelegram()
  const { setTheme } = useThemeStore()

  useEffect(() => {
    // Notify Telegram Mini App is ready
    ready()
    expand()

    // Respect telegram color scheme if present
    const isDark = window.Telegram?.WebApp?.colorScheme === 'dark' || true
    setTheme(isDark ? 'dark' : 'light')
  }, [ready, expand, setTheme])

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<HomePage />} />
          <Route path="habits" element={<HabitsPage />} />
          <Route path="growth" element={<GrowthPage />} />
          <Route path="journal" element={<JournalPage />} />
          <Route path="ai" element={<AICoachPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="spiritual" element={<SpiritualPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
