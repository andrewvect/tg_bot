import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, VStack, Stack, Box, Center} from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import { CardComponent } from '../components/Card/card'
import Loading from '../components/Common/Loading'
import { AbsoluteCenter } from "@chakra-ui/react"
import { Legend } from '../components/Card/legend'
import { useNewWordsPresenter } from '../presenters/useNewWordsPresenter'

export const Route = createFileRoute('/new')({
    component: NewWord,
})

function NewWord() {
    const navigate = useNavigate()
    const { words, loading, currentWord, handleAddCard, handleSkipCard } = useNewWordsPresenter()

    if (loading) {
        return <Loading />
    }

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

    return (
        <BackgroundBox>
            <Center>
            <VStack maxWidth="300px" alignItems={"center"} justifyContent="center">
            <Box height="20vh"/>

            <Legend header={currentWord?.legend ?? ''} sentences={[currentWord]} alphabetSettings={null} />

            <VStack spacing={6} width="100%" alignItems="center" justifyContent="center">

                    <Box height="2vw">
                    </Box>

                    <VStack alignItems="center" justifyContent="center">
                        <CardComponent header={`${currentWord?.cyrillic_word ?? ''}/${currentWord?.latin_word ?? ''}`}>
                            {currentWord?.native_word ?? ''}
                        </CardComponent>
                    </VStack>
                    <VStack spacing={1} alignItems="center" width="100%" bottom="15vh" position={"absolute"}>
                        <Stack direction="row" spacing="-15vw" width="100%">
                            <Button variant="primary" width="50%" onClick={handleAddCard}>
                                Добавить
                            </Button>
                            <Button variant="primary" width="50%" onClick={handleSkipCard}>
                                Уже знаю
                            </Button>
                        </Stack>
                        <Box height="5vh"/>
                        <Button variant="primary" width="100%" onClick={() => navigate({ to: '/main' })}>
                            Назад в меню
                        </Button>
                    </VStack>
            </VStack>
            </VStack>
            </Center>


        </BackgroundBox>
    )
}

export default NewWord
