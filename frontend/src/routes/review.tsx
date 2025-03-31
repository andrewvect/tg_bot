import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, AbsoluteCenter, VStack, Stack, Progress, Box } from "@chakra-ui/react"

import { ViewIcon, CheckIcon, CloseIcon } from "@chakra-ui/icons"
import BackgroundBox from '../components/back'
import { CardComponent } from '../components/Card/card'
import { UtilsService, SettingsService } from '../client/sdk.gen'
import { WordsResponse } from '../client/types.gen'
import {useState, useEffect} from 'react'
import AllWordsReviewed from '../components/AllWordsReviewed'
import Loading from '../components/Common/Loading' // added Loading import

export const Route = createFileRoute('/review')({
    component: ReviewPage,
})

async function fetchReviewWords() {
    const token = localStorage.getItem('token')

    // Fetch words from API
    const response = await UtilsService.getReviewWords({
        authorization: `Bearer ${token}`
    })

    if (!response.words || response.words.length === 0) {
        return [];
    }

    return response.words;
}

async function submitReview(data: { passed: boolean; word_id: number }): Promise<void> {
    const token = localStorage.getItem('token')
    if (!token) {
        throw new Error('No token found')
    }
    await UtilsService.addReview({
        authorization: `Bearer ${token}`,
        requestBody: {
            passed: data.passed,
            word_id: data.word_id
        }
    })
}

async function fetchUserSettings() {
    const token = localStorage.getItem('token')
    if (!token) {
        throw new Error('No token found')
    }
    return SettingsService.getUserSettings({
        authorization: `Bearer ${token}`
    })
}

async function getReviewWordsCount() {
    const token = localStorage.getItem('token')
    if (!token) {
        throw new Error('No token found')
    }
    return UtilsService.getReviewWordsCount({
        authorization: `Bearer ${token}`
    })
}

function ReviewPage() {

    const [reviewWordsCount, setCount] = useState(0)
    const [isLoading, setLoading] = useState(true)
    const [refreshKey, setRefreshKey] = useState(0)
    const [progresBar, setProgresBar] = useState(0)
    const [userSettings, setUserSettings] = useState<{ spoiler_settings: number } | null>(null)

    useEffect(() => {
        fetchUserSettings().then((settings) => {
            setUserSettings(settings)
        })
        getReviewWordsCount()
        .then((count: number) => {
            setCount(count);
            setLoading(false);
            setProgresBar(count)
        })

    }, [])

    if (isLoading) {
        return <Loading />;
    }

    if (reviewWordsCount === 0) {
        return <AllWordsReviewed />;
    }

    return <ReviewWords key={refreshKey}
    reviewWordsCount={reviewWordsCount}
    setLoading={setLoading}
    setCount={setCount}
    setRefreshKey={setRefreshKey}
    progressBar={progresBar} spoilerSettings={userSettings?.spoiler_settings?? 0} />;
}


interface ReviewWordsProps {
    reviewWordsCount: number;
    setCount: React.Dispatch<React.SetStateAction<number>>;
    setLoading: React.Dispatch<React.SetStateAction<boolean>>;
    setRefreshKey: React.Dispatch<React.SetStateAction<number>>;
    spoilerSettings: number;
    progressBar: number;
}

function ReviewWords({ reviewWordsCount, setCount, setLoading, setRefreshKey, progressBar, spoilerSettings }: ReviewWordsProps) {
    const navigate = useNavigate()
    const [words, setWords] = useState<WordsResponse['words']>([])
    const [showTranslation, setShowTranslation] = useState<{ [key: number]: boolean }>({})
    const currentWord = words[0]
    const [isProcessing, setIsProcessing] = useState(false)

    useEffect(() => {
        fetchReviewWords().then((words) => {
            setWords(words)
            setLoading(false)
        })
    }, [])

    const handleReview = (passed: boolean) => {
        if (isProcessing || !currentWord) return

        setIsProcessing(true)
        submitReview({ passed, word_id: currentWord.word_id })
          .then(() => {
            if (passed) {
                setCount(reviewWordsCount - 1)
            }
            const newWords = words.slice(1)
            setWords(newWords)

            if (newWords.length === 0) {
                setRefreshKey(prev => prev + 1)
            }
            setIsProcessing(false)
          })
          .catch(err => {
            console.error(err)
            setIsProcessing(false)
          })
    }

    // Apply spoiler settings only if currentWord exists
    let displayWord = currentWord?.word || '';
    let displayTranslation = currentWord?.translation || '';

    if (currentWord) {
        if (spoilerSettings === 2) {
            displayTranslation = currentWord.word;
            displayWord = currentWord.translation;
        } else if (spoilerSettings === 3) {
            const random = Math.random();
            if (random < 0.5) {
                displayTranslation = currentWord.word;
            } else {
                displayWord = currentWord.translation;
            }
        }
    }

    if (!currentWord) {
        return <Loading />;
    }

    return (
        <BackgroundBox>
            <AbsoluteCenter>
                <CardComponent header={displayWord}>
                    {showTranslation[currentWord.word_id] && (
                        <Text fontSize={'5xl'} color="white">
                            {displayTranslation}
                        </Text>
                    )}
                    <Button
                        onClick={() => setShowTranslation(prev => ({ ...prev, [currentWord.word_id]: true }))}
                        hidden={showTranslation[currentWord.word_id]}
                        isDisabled={isProcessing}
                    >
                        <ViewIcon />
                    </Button>
                </CardComponent>
                <VStack spacing={1} width="300px" mt="5px">
                    <Stack direction='row' width="100%">
                        <Button variant='primary' width="50%" onClick={() => handleReview(true)} isDisabled={isProcessing}>
                            <CheckIcon boxSize="6" strokeWidth="2px" />
                        </Button>
                        <Button variant='primary' width="50%" onClick={() => handleReview(false)} isDisabled={isProcessing}>
                            <CloseIcon boxSize="6" strokeWidth="2px" />
                        </Button>
                    </Stack>
                    <Button variant='primary' width="100%" onClick={() => navigate({ to: '/main' })}>Назад в меню</Button>
                </VStack>
                <Progress
                    value={reviewWordsCount}
                    max={progressBar}
                    mt="5"
                    height="1px"
                    sx={{
                        bg: 'black',
                        '& > div': {
                            bg: 'white',
                        },
                    }}
                />
            <VStack>
            <Box>
                <Text color='white'>
                    {reviewWordsCount}
                </Text>
            </Box>
            </VStack>
            </AbsoluteCenter>


        </BackgroundBox>
    )
}
