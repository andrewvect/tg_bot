from pydantic import BaseModel, Field


class SettingsUpdateRequest(BaseModel):
    spoiler_settings: int = Field(..., ge=1, le=3, description="Must be 1, 2, or 3")
    alphabet_settings: int = Field(..., ge=1, le=3, description="Must be 1, 2, or 3")


class SettingsResponse(BaseModel):
    spoiler_settings: int
    user_id: int
    alphabet_settings: int
