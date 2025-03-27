from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api.deps import get_session
from app.common.db.repositories import SettingsRepo, UserRepo
from app.common.db.repositories.user import NewUser
from app.states.user import build_user_state

router = Router()


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    """Send a message when the command /start is issued."""
    session = await anext(get_session())
    user_repo = UserRepo(session=session)
    settings_repo = SettingsRepo(session=session)
    try:
        await user_repo.create(
            user_name=message.from_user.username, telegram_id=message.from_user.id
        )
    except NewUser:
        await settings_repo.create_or_update_settings(user_id=message.from_user.id)
        await message.reply(
            f"Hi {message.from_user.username}! 👋\n"
            "Welcome, i am glad to see you new user!"
        )
        states = await build_user_state()
        states.add_new_user(user_id=message.from_user.id)
    else:
        await message.reply(f"Hi {message.from_user.username}! 👋\nWelcome back!")


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Start the bot and get a welcome message\n"
        "/help - Show this help message\n"
    )
    await message.reply(help_text)
