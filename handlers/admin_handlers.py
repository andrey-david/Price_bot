from pathlib import Path
import logging

from sqlalchemy import select, func
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from database import async_session, User

logger = logging.getLogger(__name__)
admin_router = Router()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "bot.log"


@admin_router.message(Command("status"))
async def admin_status(message: Message):
    async with async_session() as session:
        users_count = await session.scalar(
            select(func.count(User.id))
        )

    await message.answer(
        f"👤 Users: {users_count}"
    )


@admin_router.message(Command("logs"))
async def admin_logs(message: Message):
    if not LOG_FILE.exists():
        await message.answer("❌ Файл bot.log не найден")
        return

    await message.answer_document(
        document=FSInputFile(LOG_FILE)
    )
