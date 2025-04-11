from fastapi import APIRouter, Depends

from app.api.deps import SettingsRepoDep, verify_token
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
async def get_user_settings(
    settings_repo: SettingsRepoDep,
    user_id: int = Depends(verify_token),
):
    """Get user settings"""

    user = await settings_repo.get_by_condition(
        condition=settings_repo.type_model.user_id == user_id
    )
    return SettingsResponse(
        spoiler_settings=user.spoiler_settings,
        user_id=user.user_id,
        alphabet_settings=user.alphabet_settings,
    )


@router.put("/", response_model=SettingsResponse)
async def set_user_settings(
    settings_repo: SettingsRepoDep,
    request: SettingsUpdateRequest,
    user_id: int = Depends(verify_token),
):
    """Set user settings"""

    current_settings = await settings_repo.get_by_condition(
        condition=settings_repo.type_model.user_id == user_id
    )
    if (
        current_settings.spoiler_settings != request.spoiler_settings
        or current_settings.alphabet_settings != request.alphabet_settings
    ):
        current_settings.spoiler_settings = request.spoiler_settings
        current_settings.alphabet_settings = request.alphabet_settings
        user_settings = await settings_repo.update(current_settings)
    else:
        user_settings = current_settings
    return SettingsResponse(
        spoiler_settings=user_settings.spoiler_settings,
        user_id=user_settings.user_id,
        alphabet_settings=user_settings.alphabet_settings,
    )
