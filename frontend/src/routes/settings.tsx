import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, AbsoluteCenter, VStack, Stack, List, ListItem, Radio, RadioGroup } from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import { useState, useEffect } from 'react'
import { SettingsService } from '../client/sdk.gen'
import type {
    SettingsGetUserSettingsResponse,
} from '../client/types.gen'
import Loading from '../components/Common/Loading' // Import the Loading component

export const Route = createFileRoute('/settings')({
    component: NewWord,
})

// Starting levels offered to the user: word frequency-rank bands the word
// list is imported in (see backend/app/scripts/parse_git_words.py files).
const START_WORD_RANK_OPTIONS = [0, 1000, 2000, 3000]

function NewWord() {
    const navigate = useNavigate()
    const [displaySetting, setDisplaySetting] = useState('4') // Default value
    const [alphabetSetting, setAlphabetSetting] = useState('4') // Default value
    const [startWordRank, setStartWordRank] = useState('0') // Default value
    const [loading, setLoading] = useState(true) // New loading state

    useEffect(() => {
        SettingsService.getUserSettings()
            .then((res: SettingsGetUserSettingsResponse) => {
                setDisplaySetting(String(res.spoiler_settings))
                setAlphabetSetting(String(res.alphabet_settings))
                setStartWordRank(String(res.start_word_rank))
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false)) // Set loading to false after fetching
    }, [])

    const handleChange = async (
        spoilerSettingValue?: string,
        alphabetSettingsValue?: string,
        startWordRankValue?: string,
    ) => {
        const newDisplay = spoilerSettingValue !== undefined ? spoilerSettingValue : displaySetting;
        const newAlphabet = alphabetSettingsValue !== undefined ? alphabetSettingsValue : alphabetSetting;
        const newStartWordRank = startWordRankValue !== undefined ? startWordRankValue : startWordRank;
        setDisplaySetting(newDisplay);
        setAlphabetSetting(newAlphabet);
        setStartWordRank(newStartWordRank);
        try {
            await SettingsService.setUserSettings({
                requestBody: {
                    spoiler_settings: Number(newDisplay),
                    alphabet_settings: Number(newAlphabet),
                    start_word_rank: Number(newStartWordRank),
                }
            });
        } catch (err) {
            console.error(err);
        }
    }

    if (loading) {
        return <Loading /> // Render the Loading component while loading
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
                                <RadioGroup value={displaySetting} onChange={(value) => handleChange(value, undefined)}>
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
                                <RadioGroup value={alphabetSetting} onChange={(value) => handleChange(undefined, value)}>
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
                                <RadioGroup
                                    value={startWordRank}
                                    onChange={(value) => handleChange(undefined, undefined, value)}
                                >
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
