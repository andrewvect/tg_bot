from aiogram import Dispatcher

from app.api.bot.commands import router as commands_router

dispatcher = Dispatcher()
dispatcher.include_router(commands_router)
