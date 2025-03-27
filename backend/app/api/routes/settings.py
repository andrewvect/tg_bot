from fastapi import APIRouter, Header, HTTPException

from app.api.deps import SettingsRepoDep, TokensServiceDep
from app.schemas.settings import SetSettingsRequest, SettingsResponse
from app.utils.logger import logger

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
async def get_user_settings(
    settings_repo: SettingsRepoDep,
    tokens_service: TokensServiceDep,
    authorization: str = Header(None),
):
    """Get user settings"""
    try:
        user_id = tokens_service.verify_access_token(token=authorization)
        user = await settings_repo.get_by_condition(
            condition=settings_repo.type_model.user_id == user_id
        )
        return SettingsResponse(
            spoiler_settings=user.spoiler_settings, user_id=user.user_id
        )
    except Exception as e:
        logger.error("Error while getting user settings: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.put("/", response_model=SettingsResponse)
async def set_user_settings(
    settings_repo: SettingsRepoDep,
    tokens_service: TokensServiceDep,
    request: SetSettingsRequest,
    authorization: str = Header(None),
):
    """Set user settings"""
    try:
        user_id = tokens_service.verify_access_token(token=authorization)
        current_settings = await settings_repo.get_by_condition(
            condition=settings_repo.type_model.user_id == user_id
        )
        current_settings.spoiler_settings = request.spoiler_settings
        user_settings = await settings_repo.update(current_settings)
        return SettingsResponse(
            spoiler_settings=user_settings.spoiler_settings,
            user_id=user_settings.user_id,
        )
    except Exception as e:
        logger.error("Error while setting user settings: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e
