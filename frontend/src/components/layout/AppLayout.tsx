import React, { useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Header } from './Header'
import { BottomNav } from './BottomNav'

export const AppLayout: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const backBtn = window.Telegram?.WebApp?.BackButton
    if (!backBtn) return

    if (location.pathname !== '/') {
      backBtn.show()
      const handleBack = () => navigate(-1)
      backBtn.onClick(handleBack)

      return () => {
        backBtn.offClick(handleBack)
      }
    } else {
      backBtn.hide()
    }
  }, [location.pathname, navigate])

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] antialiased transition-colors">
      <Header />
      <main className="flex-1 pb-20 max-w-lg mx-auto w-full px-4 pt-4">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  )
}
