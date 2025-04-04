import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, VStack, Stack, Box } from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import { CardComponent } from '../components/Card/card'
import { UtilsService } from '../client/sdk.gen'
import { WordResponse } from '../client/types.gen'
import { useState, useEffect } from "react"
import Loading from '../components/Common/Loading' // added Loading import
import { AbsoluteCenter } from "@chakra-ui/react"

export const Route = createFileRoute('/new')({
    component: NewWord,
})

/**
 * Sends a request to create a new card with the provided data.
 *
 * @param data - The data for the new card.
 * @param data.known - Indicates whether the card is marked as known.
 * @param data.word_id - The unique identifier for the associated word.
 * @returns A promise that resolves when the new card is successfully created.
 *
 * @throws Will throw an error if no token is found in local storage.
 */
async function addNewCard(data: { known: boolean; word_id: number }): Promise<void> {

    const token = localStorage.getItem('token')
    if (!token) {
        throw new Error('No token found')
    }
    await UtilsService.newCard({
        authorization: `Bearer ${token}`,
        requestBody: {
            known: data.known,
            word_id: data.word_id
        }
    })
}

function NewWord() {
    const navigate = useNavigate()
    const [words, setWords] = useState<WordResponse[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadWords()
    }, [])

    async function loadWords(optionalInt?: number) {
        setLoading(true)

        const token = localStorage.getItem('token')

        if (!optionalInt) {
        try {
            const response = await UtilsService.getNewWord({ authorization: `Bearer ${token}` })
            if (response.words.length > 0) {
                localStorage.setItem('new_words', JSON.stringify(response.words))
                setWords(response.words)
            } else {
                localStorage.setItem('new_words', JSON.stringify([]))
                setWords([])
            }
        } catch (error: any) {
            if (error.response?.status === 400) {
                localStorage.setItem('new_words', JSON.stringify([]))
                setWords([])
            }
        } finally {
            setLoading(false)
        }
        } else {
            try {
                const response = await UtilsService.getNewWord({ authorization: `Bearer ${token}` })
                if (response.words.length > 0) {
                    localStorage.setItem('new_words', JSON.stringify(response.words))
                    setWords(response.words)
                } else {
                    localStorage.setItem('new_words', JSON.stringify([]))
                    setWords([])
                }
            } catch (error: any) {
                if (error.response?.status === 400) {
                    localStorage.setItem('new_words', JSON.stringify([]))
                    setWords([])
                }
            } finally {
                setLoading(false)
            }
        }
    }

    if (loading) {
        return <Loading />  // replaced inline loading UI with Loading component
    }

    // Make the congratulation condition clearer
    if (words.length === 0) {
      return (
        <BackgroundBox>
          <AbsoluteCenter>
            <CardComponent header="Поздравляем!">
              <Text color="white" fontSize="xl" textAlign="center">
                🥳 Вы прошли все слова в базе данных!
              </Text>
              <Button
                variant='primary'
                width="100%"
                onClick={() => navigate({ to: '/main' })}
              >
                Назад в меню
              </Button>
            </CardComponent>
          </AbsoluteCenter>
        </BackgroundBox>
      );
    }

    const currentWord = words[0]

    const handleAddCard = async () => {
        // handle "Добавить" button for adding new card
        if (currentWord) {
            await addNewCard({ known: false, word_id: currentWord.word_id })
            updateLocalWords()
        }
    }

    const handleSkipCard = async () => {
        if (currentWord) {
            await addNewCard({ known: true, word_id: currentWord.word_id })
            updateLocalWords()
        }
    }

    function updateLocalWords() {
        const newList = words.slice(1)
        localStorage.setItem('new_words', JSON.stringify(newList))
        setWords(newList)
        if (newList.length < 2) {
            loadWords(2)
        }
    }

    return (
        <BackgroundBox>
            <AbsoluteCenter>
                <VStack>
                <CardComponent header={currentWord?.translation ?? ''}>

                    {currentWord?.word ?? ''}

                </CardComponent>
                <Box height="40px" />
                <VStack spacing={1} width="300px" mt="5px" align="center">
                    <Stack direction='row' width="100%">
                        <Button variant='primary' width="50%" onClick={handleAddCard}>Добавить</Button>
                        <Button variant='primary' width="50%" onClick={handleSkipCard}>Уже знаю</Button>
                    </Stack>
                    <Button
                        variant='primary'
                        width="100%"
                        onClick={() => navigate({ to: '/main' })}
                    >
                        Назад в меню
                    </Button>
                </VStack>
                </VStack>
            </AbsoluteCenter>
        </BackgroundBox>
    )
}

export default NewWord
