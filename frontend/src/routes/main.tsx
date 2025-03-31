import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, VStack, Container, Box, AbsoluteCenter, Circle } from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import { useEffect, useState } from 'react'
import { UtilsService } from '../client/sdk.gen'

export const Route = createFileRoute('/main')({
    component: () => <Main />,
})

function Main() {
    const navigate = useNavigate()
    const [reviewCount, setReviewCount] = useState<string>('0')

    useEffect(() => {
        const token = localStorage.getItem('token')
        if (token) {
            UtilsService.getReviewWordsCount({
                authorization: `Bearer ${token}`
            })
            .then(response => {
                const count = response ?? 0;
                const reviewWordsCount = String(count);
                setReviewCount(reviewWordsCount);
            })
            .catch(error => console.error('Error fetching word count:', error))
        }
    }, [])

    return (
        <BackgroundBox>
            <Container>
                <AbsoluteCenter>
                    <VStack spacing={5} width="300px" height="200px">
                        <Button variant='primary' width="100%" onClick={() => navigate({ to: '/new' })}>
                            Добавить новые слова
                        </Button>
                        <Box position="relative" width="100%">
                            <Button variant='primary' width="100%" onClick={() => navigate({ to: '/review' })}>
                                Повторить слова
                            </Button>
                            <Circle
                                size="6"
                                bg="red"
                                color="white"
                                position="absolute"
                                top="-2"
                                right="-2"
                            >
                                {reviewCount}
                            </Circle>
                        </Box>
                        <Button variant='primary' width="100%" onClick={() => navigate({ to: '/settings' })}>
                            Настройки
                        </Button>
                    </VStack>
                </AbsoluteCenter>
            </Container>
        </BackgroundBox>
    )
}
