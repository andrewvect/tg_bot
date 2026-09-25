import { useEffect, useState } from 'react'
import { UtilsService } from '../client/sdk.gen'
import type { WordResponse } from '../client/types.gen'
import { newWordsStorage, tokenStorage } from '../services/localStorage'

async function addNewCard(data: { known: boolean; word_id: number }): Promise<void> {
    if (!tokenStorage.get()) {
        throw new Error('No token found')
    }
    await UtilsService.newCard({
        requestBody: {
            known: data.known,
            word_id: data.word_id,
        },
    })
}

export function useNewWordsPresenter() {
    const [words, setWords] = useState<WordResponse[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadWords()
    }, [])

    async function loadWords() {
        setLoading(true)
        try {
            const response = await UtilsService.getNewWord()
            const newWords = response.words.length > 0 ? response.words : []
            newWordsStorage.set(newWords)
            setWords(newWords)
        } catch (error: any) {
            if (error.response?.status === 400) {
                newWordsStorage.set([])
                setWords([])
            }
        } finally {
            setLoading(false)
        }
    }

    function updateLocalWords() {
        const newList = words.slice(1)
        newWordsStorage.set(newList)
        setWords(newList)
        if (newList.length < 2) {
            loadWords()
        }
    }

    const currentWord = words[0]

    const handleAddCard = async () => {
        if (!currentWord) return
        await addNewCard({ known: false, word_id: currentWord.word_id })
        updateLocalWords()
    }

    const handleSkipCard = async () => {
        if (!currentWord) return
        await addNewCard({ known: true, word_id: currentWord.word_id })
        updateLocalWords()
    }

    return { words, loading, currentWord, handleAddCard, handleSkipCard }
}
