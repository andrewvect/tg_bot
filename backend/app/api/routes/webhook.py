"""Webhook routes for handling Telegram bot updates."""

from fastapi import APIRouter, Request, Response
from aiogram import Bot, types
from aiogram.client.telegram import TEST

import traceback
from typing import TypedDict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from app.utils.logger import logger
from app.core.config import settings

from app.api.bot.main import dispatcher


router = APIRouter(prefix="/webhook", tags=["webhook"])


class TransferData(TypedDict):
    """Common transfer data."""

    # user: UserEntity
    # admin: AdminEntity
    engine: AsyncEngine
    redis_url: str
    role: int


@router.post("")
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

    try:
        bot = Bot(token=settings.BOT_TOKEN)
        # bot.session.api = TEST

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
    except (ValueError, KeyError):
        logger.error("Error while processing update: %s", traceback.format_exc())
        return Response(status_code=500)

    return Response(status_code=200)
