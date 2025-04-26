"""Webhook routes for handling Telegram bot updates."""

from typing import TypedDict

from aiogram import Bot, types
from aiogram.client.telegram import TEST
from fastapi import APIRouter, Request, Response
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.api.bot.main import dispatcher
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["webhook"])


class TransferData(TypedDict):
    """Common transfer data."""

    # user: UserEntity
    # admin: AdminEntity
    engine: AsyncEngine
    redis_url: str
    role: int


@router.post("/")
async def webhook(request: Request) -> Response:
    """Handle incoming updates from Telegram bot.

    Args:
        request: FastAPI request object containing the update from Telegram

    Returns:
        Response with appropriate status code
    """
    update = await request.json()
    update = types.Update(**update)

    bot = Bot(token=settings.BOT_TOKEN)
    if settings.ENVIRONMENT == "local":
        # For local testing, set the bot to TEST mode
        bot.session.api = TEST
    try:
        await dispatcher.feed_update(
            update=update,
            bot=bot,
            config=settings,
            **TransferData(
                logger=logger,
                engine=create_async_engine(
                    url=settings.ASYNC_SQLALCHEMY_DATABASE_URI,
                    pool_size=10,
                    max_overflow=5,
                    pool_timeout=30,
                    pool_recycle=1800,
                ),
            ),
            redis_url="",
        )

        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return Response(status_code=200)
