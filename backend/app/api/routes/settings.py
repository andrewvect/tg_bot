from fastapi import APIRouter, Depends

from app.api.deps import SettingsServiceDep, verify_token  # updated import
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
async def get_user_settings(
    settings_service: SettingsServiceDep,
    user_id: int = Depends(verify_token),
) -> SettingsResponse:
    """Get user settings"""
    user = await settings_service.get_user_settings(user_id)
    return SettingsResponse(
        spoiler_settings=user.spoiler_settings,
        user_id=user.user_id,
        alphabet_settings=user.alphabet_settings,
    )


@router.put("/", response_model=SettingsResponse)
async def set_user_settings(
    request: SettingsUpdateRequest,
    settings_service: SettingsServiceDep,
    user_id: int = Depends(verify_token),
) -> SettingsResponse:
    """Set user settings"""
    user = await settings_service.update_user_settings(user_id, request)
    return SettingsResponse(
        spoiler_settings=user.spoiler_settings,
        user_id=user.user_id,
        alphabet_settings=user.alphabet_settings,
    )
