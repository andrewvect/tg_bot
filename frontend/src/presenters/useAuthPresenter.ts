import { useNavigate } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { LoginService } from '../client/sdk.gen'
import { clearWordCaches, tokenStorage } from '../services/localStorage'

interface TelegramWebApp {
  initData: string
}

interface Telegram {
  WebApp: TelegramWebApp
}

declare global {
  interface Window {
    Telegram: Telegram
  }
}

export function useAuthPresenter() {
  const navigate = useNavigate()
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    const handleTelegramAuth = async () => {
      if (!window.Telegram?.WebApp) {
        setErrorMessage('Telegram WebApp is not available')
        return
      }

      try {
        const response = await LoginService.loginAccessToken({
          requestBody: {
            init_data: window.Telegram.WebApp.initData,
          },
        })

        if (response.access_token) {
          tokenStorage.set(response.access_token)
          clearWordCaches()
          navigate({ to: '/main' })
        }
      } catch (error) {
        setErrorMessage(`Login failed: ${error}`)
      }
    }

    handleTelegramAuth()
  }, [navigate])

  return { errorMessage }
}
