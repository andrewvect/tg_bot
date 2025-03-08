from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    get_tokens_service,
)
from app.core import security
from app.core.config import settings
from app.token_service import TokensService
from app.schemas.telegram_auth import RequestInitData, ResponceToken

router = APIRouter(tags=["login"])


@router.post("/login/access-token", response_model=ResponceToken)
def login_access_token(
    request: RequestInitData,
    tokens_service: TokensService = Depends(get_tokens_service),
) -> ResponceToken:

    try:
        user_id = tokens_service.verify(init_data=request.init_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return ResponceToken(
        access_token=security.create_access_token(
            user_id, expires_delta=access_token_expires
        ),
        user_id=user_id,
        expires_in=access_token_expires.total_seconds(),
    )
