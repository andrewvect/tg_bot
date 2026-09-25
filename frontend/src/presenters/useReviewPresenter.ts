import { useEffect, useState } from 'react'
import { SettingsService, UtilsService } from '../client/sdk.gen'
import type { WordsResponse } from '../client/types.gen'

async function fetchReviewWords() {
    const response = await UtilsService.getReviewWords()
    return response.words ?? []
}

async function submitReview(data: { passed: boolean; word_id: number }): Promise<void> {
    await UtilsService.addReview({
        requestBody: {
            passed: data.passed,
            word_id: data.word_id,
            idempotency_key: crypto.randomUUID(),
        }
    })
}

export function useReviewPresenter() {
    // Session: how many words are due, and the settings that control how
    // a word card is shown.
    const [isLoading, setIsLoading] = useState(true)
    const [reviewWordsCount, setReviewWordsCount] = useState(0)
    const [progressBar, setProgressBar] = useState(0)
    const [spoilerSettings, setSpoilerSettings] = useState(0)
    const [alphabetSettings, setAlphabetSettings] = useState(0)
    const [refreshKey, setRefreshKey] = useState(0)

    // The current batch of words being reviewed.
    const [words, setWords] = useState<WordsResponse['words']>([])
    const [wordsLoading, setWordsLoading] = useState(true)
    const [showTranslation, setShowTranslation] = useState<{ [key: number]: boolean }>({})
    const [isProcessing, setIsProcessing] = useState(false)
    const [flipped, setFlipped] = useState(true)
    const [displayWord, setDisplayWord] = useState('')
    const [displayTranslation, setDisplayTranslation] = useState('')
    const [flag, setFlag] = useState('')
    const [alphabet, setAlphabet] = useState('')
    const [choosedAlphabet, setChoosedAlphabet] = useState(0)

    const currentWord = words[0]

    useEffect(() => {
        SettingsService.getUserSettings().then((settings) => {
            setSpoilerSettings(settings.spoiler_settings)
            setAlphabetSettings(settings.alphabet_settings)
        })
        UtilsService.getReviewWordsCount().then((count: number) => {
            setReviewWordsCount(count)
            setProgressBar(count)
            setIsLoading(false)
        })
    }, [])

    // Fetch the next batch once we know there's something to review, and
    // again whenever refreshKey bumps (the in-hand batch was cleared).
    useEffect(() => {
        if (isLoading || reviewWordsCount === 0) return
        setWordsLoading(true)
        fetchReviewWords().then((fetchedWords) => {
            setWords(fetchedWords)
            setWordsLoading(false)
        })
    }, [isLoading, reviewWordsCount, refreshKey])

    // Decide what to actually show for the current word (which alphabet,
    // which side is the "front", the flag) whenever it or the settings change.
    useEffect(() => {
        if (!currentWord) return

        let originalWord: string | undefined
        if (alphabetSettings === 3) {
            originalWord = currentWord.latin_word
            setChoosedAlphabet(3)
            setAlphabet('🔠')
        } else if (alphabetSettings === 2) {
            originalWord = currentWord.cyrillic_word
            setChoosedAlphabet(2)
            setAlphabet('')
        } else if (alphabetSettings === 1) {
            if (Math.random() < 0.5) {
                originalWord = currentWord.latin_word
                setChoosedAlphabet(3)
                setAlphabet('🔠')
            } else {
                originalWord = currentWord.cyrillic_word
                setChoosedAlphabet(2)
                setAlphabet('')
            }
        }

        const originalTranslation = currentWord.native_word
        if (flipped) {
            if (spoilerSettings === 1) {
                setDisplayWord(originalTranslation)
                setDisplayTranslation(originalWord ?? '')
                setFlag('🇷🇺')
                setAlphabet('')
            } else if (spoilerSettings === 3) {
                if (Math.random() < 0.5) {
                    setDisplayWord(originalTranslation)
                    setDisplayTranslation(originalWord ?? '')
                    setFlag('🇷🇺')
                    setAlphabet('')
                } else {
                    setDisplayWord(originalWord ?? '')
                    setDisplayTranslation(originalTranslation)
                    setFlag('🇷🇸')
                }
            } else {
                setDisplayWord(originalWord ?? '')
                setDisplayTranslation(originalTranslation)
                setFlag('🇷🇸')
            }
        } else {
            setDisplayWord(originalWord ?? '')
            setDisplayTranslation(originalTranslation)
            setFlag('🇷🇸')
        }
    }, [currentWord, choosedAlphabet, spoilerSettings, flipped])

    const handleReview = (passed: boolean) => {
        if (isProcessing || !currentWord) return

        setIsProcessing(true)
        submitReview({ passed, word_id: currentWord.word_id })
            .then(() => {
                if (passed) {
                    setReviewWordsCount((count) => count - 1)
                }
                const newWords = words.slice(1)
                setWords(newWords)
                if (newWords.length === 0) {
                    setRefreshKey((key) => key + 1)
                }
                setIsProcessing(false)
            })
            .catch((err) => {
                console.error(err)
                setIsProcessing(false)
            })
    }

    const revealTranslation = () => {
        if (!currentWord) return
        setShowTranslation((prev) => ({ ...prev, [currentWord.word_id]: true }))
        setFlipped(true)
    }

    return {
        isLoading,
        reviewWordsCount,
        progressBar,
        wordsLoading,
        currentWord,
        showTranslation,
        isProcessing,
        displayWord,
        displayTranslation,
        flag,
        alphabet,
        choosedAlphabet,
        handleReview,
        revealTranslation,
    }
}
