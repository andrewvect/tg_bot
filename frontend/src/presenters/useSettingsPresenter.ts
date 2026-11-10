import { useEffect, useState } from 'react'
import { SettingsService } from '../client/sdk.gen'
import type { SettingsGetUserSettingsResponse } from '../client/types.gen'

// Starting levels offered to the user: word frequency-rank bands the word
// list is imported in (see backend/app/scripts/parse_git_words.py files).
export const START_WORD_RANK_OPTIONS = [0, 1000, 2000, 3000]

export function useSettingsPresenter() {
    const [displaySetting, setDisplaySetting] = useState('4')
    const [alphabetSetting, setAlphabetSetting] = useState('4')
    const [startWordRank, setStartWordRank] = useState('0')
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        SettingsService.getUserSettings()
            .then((res: SettingsGetUserSettingsResponse) => {
                setDisplaySetting(String(res.spoiler_settings))
                setAlphabetSetting(String(res.alphabet_settings))
                setStartWordRank(String(res.start_word_rank))
            })
            .catch(err => console.error(err))
            .finally(() => setLoading(false))
    }, [])

    const handleChange = async (
        spoilerSettingValue?: string,
        alphabetSettingsValue?: string,
        startWordRankValue?: string,
    ) => {
        const newDisplay = spoilerSettingValue !== undefined ? spoilerSettingValue : displaySetting
        const newAlphabet = alphabetSettingsValue !== undefined ? alphabetSettingsValue : alphabetSetting
        const newStartWordRank = startWordRankValue !== undefined ? startWordRankValue : startWordRank
        setDisplaySetting(newDisplay)
        setAlphabetSetting(newAlphabet)
        setStartWordRank(newStartWordRank)
        try {
            await SettingsService.setUserSettings({
                requestBody: {
                    spoiler_settings: Number(newDisplay),
                    alphabet_settings: Number(newAlphabet),
                    start_word_rank: Number(newStartWordRank),
                }
            })
        } catch (err) {
            console.error(err)
        }
    }

    return {
        loading,
        displaySetting,
        alphabetSetting,
        startWordRank,
        setDisplaySetting: (value: string) => handleChange(value, undefined),
        setAlphabetSetting: (value: string) => handleChange(undefined, value),
        setStartWordRank: (value: string) => handleChange(undefined, undefined, value),
    }
}
