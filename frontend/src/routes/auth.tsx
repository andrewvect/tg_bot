import { createFileRoute } from '@tanstack/react-router'
import { Alert } from "@chakra-ui/react"
import { useAuthPresenter } from '../presenters/useAuthPresenter'

export const Route = createFileRoute('/auth')({
  component: AuthPage
})

function AuthPage() {
  const { errorMessage } = useAuthPresenter()

  return (
    <>
      {errorMessage && <Alert status="error">{errorMessage}</Alert>}
      <div>Authenticating...</div>
    </>
  )
}
