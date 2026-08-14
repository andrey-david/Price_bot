import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from keyboards import (
    regions_keyboard,
    regions_keyboard_no_back,
)
from database import (
    async_session,
    User,
    Region,
)
from lexicon import (
    LEXICON,
)

logger = logging.getLogger(__name__)
handlers_region_router = Router(name='handlers_region_router')


@handlers_region_router.callback_query(F.data == "menu:regions")
async def menu_regions(
        callback: CallbackQuery,
        user: User,
        language: str
):
    async with async_session() as session:
        regions = await session.scalars(
            select(Region)
        )

        regions = regions.all()

    selected_regions = {
        region.id for region in user.regions
    }

    await callback.message.edit_text(
        text=LEXICON[language]["regions_select"],
        reply_markup=regions_keyboard(
            regions,
            selected_regions,
            language
        )
    )

    await callback.answer()


@handlers_region_router.callback_query(F.data == "start_region")
async def start_region(callback: CallbackQuery):
    async with async_session() as session:
        user = await session.scalar(
            select(User)
            .where(User.telegram_id == callback.from_user.id)
        )

        if user is None:
            await callback.answer("ERROR")
            return

        language = user.language

        regions = await session.scalars(
            select(Region)
        )

        regions = regions.all()

        await session.commit()

    selected_regions = {
        region.id for region in user.regions
    }

    await callback.message.edit_text(
        text=LEXICON[language]["regions_select"],
        reply_markup=regions_keyboard_no_back(
            regions,
            selected_regions,
            language
        )
    )

    await callback.answer()


@handlers_region_router.callback_query(
    F.data.startswith("region:")
)
async def toggle_region(callback: CallbackQuery):
    region_id = int(callback.data.split(":")[1])

    async with async_session() as session:
        user = await session.scalar(
            select(User)
            .options(selectinload(User.regions))
            .where(User.telegram_id == callback.from_user.id)
        )

        region = await session.scalar(
            select(Region)
            .where(Region.id == region_id)
        )

        if user is None or region is None:
            await callback.answer("Ошибка")
            return

        lexicon = LEXICON[user.language]

        if region in user.regions:
            user.regions.remove(region)
            text = f"{lexicon['region_removed']} {region.country}"
        else:
            max_regions = 5

            if len(user.regions) >= max_regions:
                await callback.answer(
                    lexicon["max_regions"],
                    show_alert=True
                )
                return

            user.regions.append(region)
            text = f"{lexicon['region_added']} {region.country}"

        await session.commit()

        regions = await session.scalars(
            select(Region)
        )
        regions = regions.all()

        selected_regions = {
            r.id for r in user.regions
        }

        await callback.message.edit_reply_markup(
            reply_markup=regions_keyboard(
                regions,
                selected_regions,
                user.language
            )
        )

        await callback.answer(text)
