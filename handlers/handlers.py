import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
)
from sqlalchemy import select

from keyboards import (
    find_game_keyboard,
    menu_keyboard,
    currency_keyboard,
    languages_keyboard_on_start,
    regions_keyboard_on_start,
    currency_keyboard_on_start,
)
from lexicon import (
    LEXICON,
    CURRENCIES,
)
from database import (
    async_session,
    User,
)

logger = logging.getLogger(__name__)
handlers_router = Router(name='handlers_router')


# Main --------------------------------------------------------------------
@handlers_router.message(Command(commands="start"))
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON["en"]["language"],
        reply_markup=languages_keyboard_on_start()
    )


@handlers_router.message(Command(commands="menu"))
async def process_start_command(message: Message):
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )

        language = user.language

        if user is None:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                language="ru",
            )

            session.add(user)
            await session.commit()

    await message.answer(
        LEXICON[language]["language"],
        reply_markup=menu_keyboard(language=language)
    )


@handlers_router.message(Command(commands=["help", "info"]))
async def process_help_command(
    message: Message,
    language: str
):
    await message.answer(
        LEXICON[language]["help"],
        reply_markup=find_game_keyboard(language)
    )


@handlers_router.callback_query(F.data == "back:menu")
async def back_menu(
        callback: CallbackQuery,
        language: str
):
    await callback.message.edit_text(
        text=LEXICON[language]["menu"],
        reply_markup=menu_keyboard(language=language)
    )
    await callback.answer()


# Language --------------------------------------------------------------------
@handlers_router.callback_query(F.data.startswith("language:"))
async def select_language(callback: CallbackQuery):
    language = callback.data.split(":")[1]

    async with async_session() as session:
        user = await session.scalar(
            select(User)
            .where(User.telegram_id == callback.from_user.id)
        )

        if user is None:
            await callback.answer("Ошибка")
            return

        user.language = language
        await session.commit()

    await callback.message.edit_text(
        text=LEXICON[language]["menu"],
        reply_markup=menu_keyboard(language)
    )

    await callback.answer()


@handlers_router.callback_query(F.data.startswith("start_language:"))
async def select_start_language(callback: CallbackQuery):
    language = callback.data.split(":")[1]

    async with async_session() as session:
        user = await session.scalar(
            select(User)
            .where(User.telegram_id == callback.from_user.id)
        )

        if user is None:
            await callback.answer("ERROR")
            return

        user.language = language
        await session.commit()

    await callback.message.edit_text(
        text=LEXICON[language]["currency"],
        reply_markup=currency_keyboard_on_start(
            CURRENCIES,
        )
    )

    await callback.answer()


# Currency --------------------------------------------------------------------
@handlers_router.callback_query(
    F.data.startswith("currency:")
)
async def select_currency(callback: CallbackQuery):
    currency = callback.data.split(":")[1]

    async with async_session() as session:
        user = await session.scalar(
            select(User)
            .where(User.telegram_id == callback.from_user.id)
        )

        if user is None:
            await callback.answer("Ошибка")
            return

        user.currency = currency
        language = user.language

        await session.commit()

    await callback.message.edit_text(
        text=LEXICON[language]["menu"],
        reply_markup=menu_keyboard(language)
    )

    await callback.answer()


@handlers_router.callback_query(F.data.startswith("start_currency:")
)
async def select_start_currency(callback: CallbackQuery):
    currency = callback.data.split(":")[1]

    async with async_session() as session:
        user = await session.scalar(
            select(User)
            .where(User.telegram_id == callback.from_user.id)
        )

        if user is None:
            await callback.answer("ERROR")
            return

        user.currency = currency
        language = user.language

        await session.commit()

    await callback.message.edit_text(
        text=LEXICON[language]["start"],
        reply_markup=regions_keyboard_on_start(language)
    )

    await callback.answer()


@handlers_router.callback_query(F.data.startswith("currency:"))
async def select_currency(
        callback: CallbackQuery,
        user: User,
        language: str
):
    currency = callback.data.split(":")[1]

    async with async_session() as session:
        user = await session.merge(user)
        user.currency = currency
        await session.commit()

    await callback.answer(
        f'{LEXICON[language]["currency_chosen"]}: {currency}'
    )

    await callback.message.edit_reply_markup(
        reply_markup=currency_keyboard(
            CURRENCIES,
            currency,
            language
        )
    )


@handlers_router.callback_query(F.data == "menu:currency")
async def menu_currency(
        callback: CallbackQuery,
        user: User,
        language: str
):
    await callback.answer()

    await callback.message.edit_text(
        text=LEXICON[language]["currency"],
        reply_markup=currency_keyboard(
            CURRENCIES,
            user.currency,
            language
        )
    )


