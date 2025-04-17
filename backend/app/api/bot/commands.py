from pathlib import Path

import yaml
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api.deps import get_session
from app.common.db.repositories import SettingsRepo, UserRepo
from app.common.db.repositories.user import NewUser
from app.states.user import build_user_state

router = Router()

# Load content from YAML file


def load_content() -> dict:
    content_path = Path(__file__).parents[3] / "content.yaml"
    with open(content_path, encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


content = load_content()
messages = content.get("messages", {})


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
            messages.get("start", {})
            .get("new_user", "")
            .format(username=message.from_user.username)
        )
        states = await build_user_state()
        states.add_new_user(user_id=message.from_user.id)
    else:
        await message.reply(
            messages.get("start", {})
            .get("returning_user", "")
            .format(username=message.from_user.username)
        )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Send a message when the command /help is issued."""
    help_text = messages.get("help", "Help information not available.")
    await message.reply(help_text)
