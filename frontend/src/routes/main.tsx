import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, VStack, Container, Box, AbsoluteCenter, Circle } from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import { useMainMenuPresenter } from '../presenters/useMainMenuPresenter'

export const Route = createFileRoute('/main')({
    component: () => <Main />,
})

function Main() {
    const navigate = useNavigate()
    const { reviewCount } = useMainMenuPresenter()

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
                                size="8"
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
