import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, Center, VStack, Stack, Progress, Box } from "@chakra-ui/react"

import { ViewIcon, CheckIcon, CloseIcon } from "@chakra-ui/icons"
import BackgroundBox from '../components/back'
import { CardComponent } from '../components/Card/card'
import AllWordsReviewed from '../components/AllWordsReviewed'
import Loading from '../components/Common/Loading'
import { Legend } from '../components/Card/legend'
import { Flag } from '../components/Card/flag'
import { useReviewPresenter } from '../presenters/useReviewPresenter'

export const Route = createFileRoute('/review')({
    component: ReviewPage,
})

function ReviewPage() {
    const navigate = useNavigate()
    const {
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
    } = useReviewPresenter()

    if (isLoading) {
        return <Loading />
    }

    if (reviewWordsCount === 0) {
        return <AllWordsReviewed />
    }

    if (wordsLoading || !currentWord) {
        return <Loading />
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
                                    onClick={revealTranslation}
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
