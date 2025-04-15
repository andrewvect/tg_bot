import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { LoginService } from '../client/sdk.gen'
import { useEffect, useState } from 'react'
import { Alert } from "@chakra-ui/react"
import { OpenAPI } from '../client/core/OpenAPI'

interface TelegramWebApp {
  initData: string;
}

interface Telegram {
  WebApp: TelegramWebApp;
}

declare global {
  interface Window {
    Telegram: Telegram;
  }
}

export const Route = createFileRoute('/auth')({
  component: AuthPage
})

function AuthPage() {
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
            init_data: window.Telegram.WebApp.initData
          }
        })

        if (response.access_token) {
          localStorage.setItem('token', response.access_token) // Store token in localStorage only
          localStorage.removeItem('review_words')
          localStorage.removeItem('new_words');

          navigate({ to: '/main' })
        }
      } catch (error) {
        setErrorMessage(`Login failed: ${error}`)
      }
    }

    handleTelegramAuth()
  }, [navigate])

  return (
    <>
      {errorMessage && <Alert status="error">{errorMessage}</Alert>}
      <div>Authenticating...</div>
    </>
  )
}
