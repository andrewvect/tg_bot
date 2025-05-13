import re
from pathlib import Path
from typing import cast

import yaml
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api.deps import async_session_factory
from app.common.db.repositories import SettingsRepo, UserRepo
from app.common.db.repositories.user import NewUser
from app.core.config import settings
from app.states.user import build_user_state
from app.utils.logger import logger

router = Router()

# Load content from YAML file


def load_content() -> dict[str, dict[str, str]]:
    # Use absolute path for Docker compatibility
    content_path = Path("/app/content.yaml")
    if not content_path.exists():
        # fallback for local dev
        content_path = Path(__file__).parents[3] / "content.yaml"
    with open(content_path, encoding="utf-8") as file:
        content_data = yaml.safe_load(file) or {}
        return cast(dict[str, dict[str, str]], content_data)


content = load_content()
messages = content.get("messages", {})


def markdown_to_html(text: str) -> str:
    """
    Convert Markdown-style formatting to HTML for Telegram.
    - **bold** becomes <b>bold</b>
    - [link text](url) becomes <a href="url">link text</a>
    """
    # Convert bold text: **text** -> <b>text</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # Convert links: [text](url) -> <a href="url">link text</a>
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)

    return text


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    """Send a message when the command /start is issued."""
    if not message.from_user:
        await message.reply("User information not available.")
        return

    from_user = message.from_user
    username = from_user.username or "User"
    user_id = from_user.id

    async with async_session_factory() as session:
        user_repo = UserRepo(session=session)
        settings_repo = SettingsRepo(session=session)
        try:
            await user_repo.create(user_name=username, telegram_id=user_id)
        except NewUser:
            logger.info(
                "User %s with ID %s registered",
                username,
                user_id,
            )
            # Notify admin about the new user registration

            if settings.ADMIN_TG_ID and message.bot:
                admin_id = settings.ADMIN_TG_ID
                bot = message.bot
                await bot.send_message(
                    admin_id,
                    f"New user registered: @{username} (ID: {user_id}). "
                    f"Contact: <a href='tg://user?id={user_id}'>Open chat</a>",
                    parse_mode="HTML",
                )
            await settings_repo.create_or_update_settings(user_id=user_id)

            start_messages = cast(dict[str, str], messages.get("start", {}))
            new_user_message = start_messages.get("new_user", "Welcome!")
            await message.reply(new_user_message.format(username=username))
            states = await build_user_state()
            states.add_new_user(user_id=user_id)
        else:
            start_messages = cast(dict[str, str], messages.get("start", {}))
            returning_user_message = start_messages.get(
                "returning_user", "Welcome back!"
            )
            await message.reply(returning_user_message.format(username=username))


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Send a message when the command /help is issued."""
    help_sections = cast(dict[str, dict[str, str]], messages.get("help", {}))

    # Send each help section as a separate message
    for section_name in ["intro", "usage", "features", "levels", "mot", "feedback"]:
        section_text = help_sections.get(section_name, "")
        if section_text and isinstance(section_text, str):
            # Convert markdown formatting to HTML
            html_text = markdown_to_html(section_text)
            await message.answer(html_text, parse_mode="HTML")
