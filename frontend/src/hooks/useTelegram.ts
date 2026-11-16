declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name: string
            last_name?: string
            username?: string
            language_code?: string
          }
        }
        colorScheme: 'light' | 'dark'
        themeParams: Record<string, string>
        isExpanded: boolean
        viewportHeight: number
        viewportStableHeight: number
        headerColor: string
        backgroundColor: string
        ready: () => void
        expand: () => void
        close: () => void
        HapticFeedback?: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void
          selectionChanged: () => void
        }
      }
    }
  }
}

export function useTelegram() {
  const tg = window.Telegram?.WebApp

  const isAvailable = Boolean(tg && tg.initData)

  const user = tg?.initDataUnsafe?.user || {
    id: 123456789,
    first_name: 'Пользователь',
    username: 'developer',
  }

  const initData = tg?.initData || 'dev_123456789'

  const impactOccurred = (style: 'light' | 'medium' | 'heavy' = 'light') => {
    tg?.HapticFeedback?.impactOccurred(style)
  }

  const notificationOccurred = (type: 'error' | 'success' | 'warning') => {
    tg?.HapticFeedback?.notificationOccurred(type)
  }

  const selectionChanged = () => {
    tg?.HapticFeedback?.selectionChanged()
  }

  return {
    tg,
    isAvailable,
    user,
    initData,
    colorScheme: tg?.colorScheme || 'dark',
    impactOccurred,
    notificationOccurred,
    selectionChanged,
    expand: () => tg?.expand(),
    close: () => tg?.close(),
    ready: () => tg?.ready(),
  }
}
