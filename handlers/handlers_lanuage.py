import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
)
from sqlalchemy import select

from keyboards import (
    menu_keyboard,
    languages_keyboard,
)
from lexicon import (
    LEXICON,
)
from database import (
    async_session,
    User,
)

logger = logging.getLogger(__name__)
handlers_language = Router(name='handlers_language')


@handlers_language.callback_query(F.data == "menu:language")
async def menu_language(
        callback: CallbackQuery,
        user: User
):
    await callback.message.edit_text(
        text=LEXICON[user.language]["language"],
        reply_markup=languages_keyboard(user.language)
    )

    await callback.answer()


@handlers_language.callback_query(F.data.startswith("language:"))
async def select_language(
        callback: CallbackQuery,
        user: User
):
    language = callback.data.split(":")[1]

    async with async_session() as session:
        db_user = await session.scalar(
            select(User)
            .where(User.telegram_id == callback.from_user.id)
        )

        db_user.language = language
        await session.commit()

    await callback.message.edit_text(
        text=LEXICON[language]["menu"],
        reply_markup=menu_keyboard(language)
    )

    await callback.answer()
