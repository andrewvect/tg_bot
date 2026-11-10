from pydantic import BaseModel, Field


class SettingsUpdateRequest(BaseModel):
    spoiler_settings: int = Field(..., ge=1, le=3, description="Must be 1, 2, or 3")
    alphabet_settings: int = Field(..., ge=1, le=3, description="Must be 1, 2, or 3")
    start_word_rank: int = Field(
        0,
        ge=0,
        multiple_of=1000,
        description="Word level to start from: 0, 1000, 2000, ...",
    )


class SettingsResponse(BaseModel):
    spoiler_settings: int
    user_id: int
    alphabet_settings: int
    start_word_rank: int
