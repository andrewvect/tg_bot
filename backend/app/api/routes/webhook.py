"""Webhook routes for handling Telegram bot updates."""

import secrets
from typing import TypedDict

from aiogram import types
from aiogram.client.telegram import TEST
from fastapi import APIRouter, Request, Response
from sqlalchemy.ext.asyncio import AsyncEngine

from app.api.bot.main import dispatcher
from app.api.deps import BotDep, engine
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["webhook"])

TELEGRAM_SECRET_TOKEN_HEADER = "X-Telegram-Bot-Api-Secret-Token"


class TransferData(TypedDict):
    """Common transfer data."""

    # user: UserEntity
    # admin: AdminEntity
    engine: AsyncEngine
    redis_url: str
    logger: object
    role: int


@router.post("/")
async def webhook(request: Request, bot: BotDep) -> Response:
    """Handle incoming updates from Telegram bot.

    Args:
        request: FastAPI request object containing the update from Telegram
        bot: Bot instance injected via dependency

    Returns:
        Response with appropriate status code
    """
    received_secret = request.headers.get(TELEGRAM_SECRET_TOKEN_HEADER, "")
    if not secrets.compare_digest(received_secret, settings.TELEGRAM_WEBHOOK_SECRET):
        logger.warning("Rejected webhook request with invalid secret token")
        return Response(status_code=401)

    update = await request.json()
    update = types.Update(**update)

    # Use telegram test environment
    if settings.TELEGRAM_TESTING:
        # For local testing, set the bot to TEST mode
        bot.session.api = TEST
    try:
        await dispatcher.feed_update(
            update=update,
            bot=bot,
            config=settings,
            **TransferData(
                logger=logger,
                engine=engine,
                redis_url="redis://localhost:6379/0",  # Providing a value for redis_url
                role=0,  # Providing a default value for role
            ),
        )

        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return Response(status_code=200)
