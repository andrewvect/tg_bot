import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, Center, VStack, Stack, Progress, Box } from "@chakra-ui/react" // replaced AbsoluteCenter with Center

import { ViewIcon, CheckIcon, CloseIcon } from "@chakra-ui/icons"
import BackgroundBox from '../components/back'
import { CardComponent } from '../components/Card/card'
import { UtilsService, SettingsService } from '../client/sdk.gen'
import { WordsResponse } from '../client/types.gen'
import {useState, useEffect} from 'react'
import AllWordsReviewed from '../components/AllWordsReviewed'
import Loading from '../components/Common/Loading' // added Loading import
import { Legend } from '../components/Card/legend'
import { Flag } from '../components/Card/flag' // new import

export const Route = createFileRoute('/review')({
    component: ReviewPage,
})

async function fetchReviewWords() {
    // Fetch words from API
    const response = await UtilsService.getReviewWords()

    if (!response.words || response.words.length === 0) {
        return [];
    }

    return response.words;
}

async function submitReview(data: { passed: boolean; word_id: number }): Promise<void> {
    await UtilsService.addReview({
        requestBody: {
            passed: data.passed,
            word_id: data.word_id
        }
    })
}

async function fetchUserSettings() {
    return SettingsService.getUserSettings()
}

async function getReviewWordsCount() {
    return UtilsService.getReviewWordsCount()
}

function ReviewPage() {

    const [reviewWordsCount, setCount] = useState(0)
    const [isLoading, setLoading] = useState(true)
    const [refreshKey, setRefreshKey] = useState(0)
    const [progresBar, setProgresBar] = useState(0)
    const [userSettings, setUserSettings] = useState<{ spoiler_settings: number, alphabet_settings: number } | null>(null)

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

    return <ReviewWords
    key={refreshKey}
    reviewWordsCount={reviewWordsCount}
    setLoading={setLoading}
    setCount={setCount}
    setRefreshKey={setRefreshKey}
    progressBar={progresBar}
    spoilerSettings={userSettings?.spoiler_settings?? 0}
    alphabetSettings={userSettings?.alphabet_settings?? 0} />;
}


interface ReviewWordsProps {
    reviewWordsCount: number;
    setCount: React.Dispatch<React.SetStateAction<number>>;
    setLoading: React.Dispatch<React.SetStateAction<boolean>>;
    setRefreshKey: React.Dispatch<React.SetStateAction<number>>;
    spoilerSettings: number;
    alphabetSettings: number;
    progressBar: number;
}

function ReviewWords({ reviewWordsCount, setCount, setLoading, setRefreshKey, progressBar, spoilerSettings , alphabetSettings}: ReviewWordsProps) {
    const navigate = useNavigate()
    const [words, setWords] = useState<WordsResponse['words']>([])
    const [showTranslation, setShowTranslation] = useState<{ [key: number]: boolean }>({})
    const currentWord = words[0]
    const [isProcessing, setIsProcessing] = useState(false)
    const [flipped, setFlipped] = useState(true)
    const [displayWord, setDisplayWord] = useState<string>('')
    const [displayTranslation, setDisplayTranslation] = useState<string>('')
    const [flag, setFlag] = useState<string>('')
    const [alphabet, setAlphabet] = useState<string>('')
    const [choosedAlphabet, setChoosedAlphabet] = useState<number>(0)

    useEffect(() => {
        fetchReviewWords().then((words) => {
            setWords(words)
            setLoading(false)
        })
    }, [])

    useEffect(() => {

        if (currentWord) {
            let originalWord;
            if (alphabetSettings === 3) {
                originalWord = currentWord.latin_word;
                setChoosedAlphabet(3);
                setAlphabet('🔠');
            } else if (alphabetSettings === 2) {
                originalWord = currentWord.cyrillic_word;
                setChoosedAlphabet(2);
                setAlphabet('');
            } else if (alphabetSettings === 1) {
                let randomNum = Math.random();

                if (randomNum < 0.5) {
                    originalWord = currentWord.latin_word;
                    setChoosedAlphabet(3);
                    setAlphabet('🔠');
                } else {
                    originalWord = currentWord.cyrillic_word;
                    setChoosedAlphabet(2);
                    setAlphabet('');
                }

                ;
            }
            let originalTranslation = currentWord.native_word;
            if (flipped) {
                if (spoilerSettings === 1) {
                    setDisplayWord(originalTranslation);
                    setDisplayTranslation(originalWord  ?? '');
                    setFlag('🇷🇺');
                    setAlphabet('')
                } else if (spoilerSettings === 3) {
                    if (Math.random() < 0.5) {
                        setDisplayWord(originalTranslation);
                        setDisplayTranslation(originalWord  ?? '');
                        setFlag('🇷🇺');
                        setAlphabet('')
                    } else {
                        setDisplayWord(originalWord ?? '');
                        setDisplayTranslation(originalTranslation);
                        setFlag('🇷🇸');
                    }
                } else {
                    setDisplayWord(originalWord  ?? '');
                    setDisplayTranslation(originalTranslation);
                    setFlag('🇷🇸');
                }
            } else {
                setDisplayWord(originalWord  ?? '');
                setDisplayTranslation(originalTranslation);
                setFlag('🇷🇸');
            }
        }
    }, [currentWord, choosedAlphabet, spoilerSettings, flipped]);

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
            <Center>
                <VStack maxWidth="300px" alignItems="center" justifyContent="center">
                    <Box height="20vh"/>

                    <Flag emoji={flag + alphabet} />

                    <Legend header={currentWord?.legend ?? ''} sentences={[currentWord]} alphabetSettings={choosedAlphabet} />
                    <Box height="5vw"/>
                    <VStack alignItems="center" justifyContent="center">
                        <CardComponent header={displayWord}>
                            {showTranslation[currentWord.word_id] ? displayTranslation :
                                <Button
                                    onClick={() => {
                                        setShowTranslation(prev => ({ ...prev, [currentWord.word_id]: true }));
                                        setFlipped(true);
                                    }}
                                    isDisabled={isProcessing}
                                    variant="outline"
                                    stroke={"grey"}
                                    borderWidth={"2px"}
                                >
                                    <ViewIcon boxSize={6} color="white" stroke="currentColor"/>
                                </Button>
                            }
                        </CardComponent>
                    </VStack>
                    <Box height="5vw" />
                    <VStack spacing={1} mt="5px" align="center" bottom="10vh" position="absolute">
                        <Stack direction='row' width="100%">
                            <Button variant='primary' width="50%" onClick={() => handleReview(true)} isDisabled={isProcessing}>
                                <CheckIcon boxSize="6" strokeWidth="4px" />
                            </Button>
                            <Button variant='primary' width="50%" onClick={() => handleReview(false)} isDisabled={isProcessing}>
                                <CloseIcon boxSize="6" strokeWidth="4px" />
                            </Button>
                        </Stack>
                        <Box height="5vw" />
                        <Box width="65vw" mt="10px">
                            <Progress
                                value={reviewWordsCount}
                                max={progressBar || 1}
                                height="2px"
                                sx={{
                                    bg: 'black',
                                    '& > div': {
                                        bg: 'white',
                                    }}
                                }
                            />
                        </Box>
                        <Text align="center" color='white'>
                            {reviewWordsCount} / {progressBar}
                        </Text>
                        <Box height="5vw" />
                        <Button variant='primary' width="100%" onClick={() => navigate({ to: '/main' })}>
                            Назад в меню
                        </Button>
                    </VStack>
                </VStack>
            </Center>
        </BackgroundBox>
    );
}
