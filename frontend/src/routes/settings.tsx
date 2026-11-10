import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, AbsoluteCenter, VStack, Stack, List, ListItem, Radio, RadioGroup } from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import Loading from '../components/Common/Loading'
import { useSettingsPresenter, START_WORD_RANK_OPTIONS } from '../presenters/useSettingsPresenter'

export const Route = createFileRoute('/settings')({
    component: SettingsPage,
})

function SettingsPage() {
    const navigate = useNavigate()
    const {
        loading,
        displaySetting,
        alphabetSetting,
        startWordRank,
        setDisplaySetting,
        setAlphabetSetting,
        setStartWordRank,
    } = useSettingsPresenter()

    if (loading) {
        return <Loading />
    }

    return (
        <BackgroundBox>
            <AbsoluteCenter>
                <VStack align="stretch" spacing={4} width="300px" p={4}>
                    <Text
                        fontSize="4xl"
                        fontWeight="bold"
                        color="white"
                        isTruncated
                        noOfLines={1}
                        textOverflow="ellipsis"
                    >
                        Настройки
                    </Text>
                    <List spacing={6}>
                        <ListItem>
                            <Stack mt={2}>
                                <Text fontSize="3xl" fontWeight="bold" color="white">Показывать первым</Text>
                                <RadioGroup value={displaySetting} onChange={setDisplaySetting}>
                                    <Stack direction="column">
                                        <Radio value="2" colorScheme="whiteAlpha">
                                            <Text fontSize="2xl" color="white">Сербское</Text>
                                        </Radio>
                                        <Radio value="1" colorScheme="whiteAlpha">
                                            <Text fontSize="2xl" color="white">Русское</Text>
                                        </Radio>
                                        <Radio value="3" colorScheme="whiteAlpha">
                                            <Text fontSize="2xl" color="white">Рандомное</Text>
                                        </Radio>
                                    </Stack>
                                </RadioGroup>
                                <Text fontSize="3xl" fontWeight="bold" color="white">Алфавит</Text>
                                <RadioGroup value={alphabetSetting} onChange={setAlphabetSetting}>
                                    <Stack direction="column">
                                        <Radio value="3" colorScheme="whiteAlpha">
                                            <Text fontSize="2xl" color="white">Латинский</Text>
                                        </Radio>
                                        <Radio value="2" colorScheme="whiteAlpha">
                                            <Text fontSize="2xl" color="white">Крилический</Text>
                                        </Radio>
                                        <Radio value="1" colorScheme="whiteAlpha">
                                            <Text fontSize="2xl" color="white">Оба</Text>
                                        </Radio>
                                    </Stack>
                                </RadioGroup>
                                <Text fontSize="3xl" fontWeight="bold" color="white">Начать со слова</Text>
                                <RadioGroup value={startWordRank} onChange={setStartWordRank}>
                                    <Stack direction="column">
                                        {START_WORD_RANK_OPTIONS.map((rank) => (
                                            <Radio key={rank} value={String(rank)} colorScheme="whiteAlpha">
                                                <Text fontSize="2xl" color="white">
                                                    {rank === 0 ? 'С начала' : `Со слова №${rank}`}
                                                </Text>
                                            </Radio>
                                        ))}
                                    </Stack>
                                </RadioGroup>
                            </Stack>
                        </ListItem>
                    </List>
                    <Button variant='primary' width="100%" mt={4} onClick={() => navigate({ to: '/main' })}>
                        Назад
                    </Button>
                </VStack>
            </AbsoluteCenter>
        </BackgroundBox>
    )
}
