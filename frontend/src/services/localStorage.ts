import type { WordResponse } from '../client/types.gen'

// Single place that owns the client-side cache keys, so screens never
// touch localStorage or its string keys directly - this is the app's
// "Model" for locally-persisted state.
const KEYS = {
  token: 'token',
  newWords: 'new_words',
  reviewWords: 'review_words',
} as const

export const tokenStorage = {
  get(): string | null {
    return localStorage.getItem(KEYS.token)
  },
  set(token: string): void {
    localStorage.setItem(KEYS.token, token)
  },
}

export const newWordsStorage = {
  get(): WordResponse[] {
    const raw = localStorage.getItem(KEYS.newWords)
    if (!raw) return []
    try {
      return JSON.parse(raw) as WordResponse[]
    } catch {
      return []
    }
  },
  set(words: WordResponse[]): void {
    localStorage.setItem(KEYS.newWords, JSON.stringify(words))
  },
}

// Clears cached word lists left over from a previous login, so a newly
// authenticated user doesn't briefly see the last user's cached words.
export function clearWordCaches(): void {
  localStorage.removeItem(KEYS.reviewWords)
  localStorage.removeItem(KEYS.newWords)
}
