import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Text, AbsoluteCenter, VStack, Stack, List, ListItem, Radio, RadioGroup } from "@chakra-ui/react"
import BackgroundBox from '../components/back'
import { useState, useEffect } from 'react'
import { SettingsService } from '../client/sdk.gen'
import type {
    SettingsGetUserSettingsResponse,
} from '../client/types.gen'

export const Route = createFileRoute('/settings')({
    component: NewWord,
})

function NewWord() {
    const navigate = useNavigate()
    const [displaySetting, setDisplaySetting] = useState('1') // Default value

    useEffect(() => {
        async function fetchSettings() {
            try {
                const token = localStorage.getItem('token')
                if (!token) {
                    console.error('No token found')
                    return
                }
                const res: SettingsGetUserSettingsResponse = await SettingsService.getUserSettings({
                    authorization: `Bearer ${token}`,
                })
                setDisplaySetting(String(res.spoiler_settings))
            } catch (err) {
                console.error(err)
            }
        }
        fetchSettings()
    }, [])

    const handleChange = async (value: string) => {
        setDisplaySetting(value)
        try {
            const token = localStorage.getItem('token')
            if (!token) {
                console.error('No token found')
                return
            }
            await SettingsService.setUserSettings({
                authorization: `Bearer ${token}`,
                requestBody: {
                    spoiler_settings: Number(value)
                }
            })
        } catch (err) {
            console.error(err)
        }
    }

    return (
        <BackgroundBox>
            <AbsoluteCenter>
                <VStack align="stretch" spacing={4} width="300px" p={4}>
                    <Text fontSize="2xl" fontWeight="bold" color="white">Настройки</Text>
                    <List spacing={6}>
                        <ListItem>
                            <Stack mt={2}>
                                <Text color="white">Показывать первым</Text>
                                <RadioGroup value={displaySetting} onChange={handleChange}>
                                    <Stack direction="column">
                                        <Radio value="2" colorScheme="whiteAlpha">
                                            <Text color="white">Сербское</Text>
                                        </Radio>
                                        <Radio value="1" colorScheme="whiteAlpha">
                                            <Text color="white">Русское</Text>
                                        </Radio>
                                        <Radio value="3" colorScheme="whiteAlpha">
                                            <Text color="white">Рандомное</Text>
                                        </Radio>
                                    </Stack>
                                </RadioGroup>
                            </Stack>
                        </ListItem>
                    </List>
                    <Button width="100%" onClick={() => navigate({ to: '/main' })}>Назад</Button>
                </VStack>
            </AbsoluteCenter>
        </BackgroundBox>
    )
}
