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
        BackButton?: {
          isVisible: boolean
          show: () => void
          hide: () => void
          onClick: (callback: () => void) => void
          offClick: (callback: () => void) => void
        }
        HapticFeedback?: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void
          selectionChanged: () => void
        }
      }
    }
  }
}

const defaultUser = {
  id: 123456789,
  first_name: 'Пользователь',
  username: 'developer',
}

const impactOccurred = (style: 'light' | 'medium' | 'heavy' = 'light') => {
  window.Telegram?.WebApp?.HapticFeedback?.impactOccurred(style)
}

const notificationOccurred = (type: 'error' | 'success' | 'warning') => {
  window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred(type)
}

const selectionChanged = () => {
  window.Telegram?.WebApp?.HapticFeedback?.selectionChanged()
}

const expand = () => {
  window.Telegram?.WebApp?.expand()
}

const close = () => {
  window.Telegram?.WebApp?.close()
}

const ready = () => {
  window.Telegram?.WebApp?.ready()
}

export function useTelegram() {
  const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : undefined
  const isAvailable = Boolean(tg && tg.initData)
  const user = tg?.initDataUnsafe?.user || defaultUser
  const initData = tg?.initData || 'dev_123456789'

  return {
    tg,
    isAvailable,
    user,
    initData,
    colorScheme: tg?.colorScheme || 'dark',
    impactOccurred,
    notificationOccurred,
    selectionChanged,
    expand,
    close,
    ready,
  }
}

