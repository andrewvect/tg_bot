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
            console.log("Fetched review words count:", count); // Debugging log
            setCount(count);
            setLoading(false);
            setProgresBar(count); // Ensure progressBar is set correctly
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
    const [flipped, setFlipped] = useState(true)
    const [displayWord, setDisplayWord] = useState<string>('')
    const [displayTranslation, setDisplayTranslation] = useState<string>('')

    useEffect(() => {
        fetchReviewWords().then((words) => {
            setWords(words)
            setLoading(false)
        })
    }, [])

    useEffect(() => {
        if (currentWord) {
            setDisplayWord(currentWord.word);
            setDisplayTranslation(currentWord.translation);
        }
        if (flipped && currentWord) {
            if (spoilerSettings === 2) {
                setDisplayTranslation(currentWord.word);
                setDisplayWord(currentWord.translation);
            } else if (spoilerSettings === 3) {
                const random = Math.random();
                if (random < 0.5) {
                    setDisplayTranslation(currentWord.word);
                    setDisplayWord(currentWord.translation);
                } else {
                    setDisplayWord(currentWord.word);
                    setDisplayTranslation(currentWord.translation);
                }
            }
        }
    }, [flipped, currentWord, spoilerSettings]);

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

    if (!currentWord) {
        return <Loading />;
    }

    return (
        <BackgroundBox>
            <AbsoluteCenter>
                <VStack  alignItems={"center"} justifyContent="center">
                <CardComponent header={displayWord}>
                    {showTranslation[currentWord.word_id] && (
                        <Text>
                            {displayTranslation}
                        </Text>
                    )}
                    <Button
                        onClick={() => {
                            setShowTranslation(prev => ({ ...prev, [currentWord.word_id]: true }));
                            setFlipped(true); // Ensure flipped is toggled correctly
                        }}
                        hidden={showTranslation[currentWord.word_id]}
                        isDisabled={isProcessing}
                    >
                        <ViewIcon />
                    </Button>
                </CardComponent>
                <VStack spacing={1} width="300px" mt="5px" align="center">
                    <Stack direction='row' width="100%">
                        <Button variant='primary' width="50%" onClick={() => handleReview(true)} isDisabled={isProcessing}>
                            <CheckIcon boxSize="6" strokeWidth="2px" />
                        </Button>
                        <Button variant='primary' width="50%" onClick={() => handleReview(false)} isDisabled={isProcessing}>
                            <CloseIcon boxSize="6" strokeWidth="2px" />
                        </Button>
                    </Stack>
                    <Box height="5vh" />
                <Box width="300px" mt="10px"> {/* Move Progress outside VStack */}
                    <Progress
                        value={reviewWordsCount}
                        max={progressBar || 1} // Fallback to prevent division by zero
                        height="2px"
                        sx={{
                            bg: 'black',
                            '& > div': {
                                bg: 'white',
                            },
                        }}
                    />
                </Box>
                <Box height="0.5vh" />

                <Text align="center" color='white'>{reviewWordsCount} / {progressBar}</Text> {/* Display progress info */}

                <Box height="1.5vh" />
                <Button variant='primary' width="100%" onClick={() => navigate({ to: '/main' })}>Назад в меню</Button>
                </VStack>
                </VStack>



            </AbsoluteCenter>
        </BackgroundBox>
    )
}
