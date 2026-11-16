import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Telegram initData to every request
apiClient.interceptors.request.use((config) => {
  const initData = window.Telegram?.WebApp?.initData || 'dev_123456789'
  if (initData) {
    config.headers.Authorization = `tma ${initData}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Graceful error logging
    console.error('API Error:', error.response?.data?.detail || error.message)
    return Promise.reject(error)
  }
)

