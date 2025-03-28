import asyncio

from aiogram import Bot

from app.core.config import settings
from app.utils.logger import logger

"""Script to set and delete Telegram webhook for the bot before star app."""


async def delete_telegram_webhook(bot) -> bool:
    try:
        result = await bot.delete_webhook()
        if result:
            logger.info("Webhook deleted successfully")
            return True
        else:
            logger.error("Failed to delete webhook")
    except Exception:
        logger.exception("Error while deleting webhook")
    return False


async def set_telegram_webhook(bot: Bot) -> bool:
    webhook_url = "https://" + settings.DOMAIN + settings.API_V1_STR + "/webhook"
    try:
        result = await bot.set_webhook(url=webhook_url)
        if result:
            logger.info("Webhook set successfully")
            return True
        else:
            logger.error("Failed to set webhook")
    except Exception:
        logger.exception("Error while setting webhook")
    return False


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    await delete_telegram_webhook(bot)
    await asyncio.sleep(1)
    await set_telegram_webhook(bot)


if __name__ == "__main__":
    asyncio.run(main())
