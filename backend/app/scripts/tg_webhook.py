import asyncio

from aiogram import Bot
from aiogram.client.telegram import TEST
from aiogram.types import MenuButtonWebApp, WebAppInfo  # added missing imports

from app.core.config import settings
from app.utils.logger import logger

"""Script to set and delete Telegram webhook for the bot before star app."""


async def delete_telegram_webhook(bot: Bot) -> bool:
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
    webhook_url = (
        "https://" + "api." + settings.DOMAIN + settings.API_V1_STR + "/webhook"
    )
    try:
        result = await bot.set_webhook(url=webhook_url)
        if result:
            logger.info(f"Webhook set successfully {webhook_url}")
            return True
        else:
            logger.error("Failed to set webhook")
    except Exception:
        logger.exception("Error while setting webhook")
    return False


async def set_telegram_web_app_url(bot: Bot) -> bool:
    try:
        if settings.TELEGRAM_TESTING:
            protocol = "http"
        else:
            protocol = "https"

        menu_button = MenuButtonWebApp(
            text="Открыть приложение",
            web_app=WebAppInfo(url=f"{protocol}://" + settings.DOMAIN + "/api/v1/auth"),
        )
        result = await bot.set_chat_menu_button(menu_button=menu_button)
        if result:
            logger.info("Telegram web app URL set successfully")

        else:
            logger.error("Failed to set Telegram web app URL")
    except Exception:
        logger.exception("Error while setting Telegram web app URL")
    return False


async def set_up_bot() -> None:
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        if settings.TELEGRAM_TESTING:
            bot.session.api = TEST

        else:
            await delete_telegram_webhook(bot)
            await asyncio.sleep(1)
            await set_telegram_webhook(bot)

        await set_telegram_web_app_url(bot)

    except Exception as e:
        logger.error(str(e))

    finally:
        await bot.session.close()
        logger.info("Bot session closed")


if __name__ == "__main__":
    asyncio.run(set_up_bot())
