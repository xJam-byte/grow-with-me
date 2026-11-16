import React from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { BottomNav } from './BottomNav'

export const AppLayout: React.FC = () => {
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
