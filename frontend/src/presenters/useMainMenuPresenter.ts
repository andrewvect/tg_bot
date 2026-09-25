import { useEffect, useState } from 'react'
import { UtilsService } from '../client/sdk.gen'
import { tokenStorage } from '../services/localStorage'

export function useMainMenuPresenter() {
  const [reviewCount, setReviewCount] = useState<string>('0')

  useEffect(() => {
    if (!tokenStorage.get()) return

    UtilsService.getReviewWordsCount()
      .then((response) => {
        setReviewCount(String(response ?? 0))
      })
      .catch((error) => console.error('Error fetching word count:', error))
  }, [])

  return { reviewCount }
}
