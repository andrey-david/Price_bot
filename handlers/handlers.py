import logging

from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from aiogram import Router

from get_prices import (
    get_prices,
    format_prices,
)
from keyboards import keyboard
from lexicon import LEXICON_RU

logger = logging.getLogger(__name__)
handlers_router = Router(name='handlers_router')


@handlers_router.message(Command(commands="start"))
async def process_start_command(message: Message):
    await message.answer(LEXICON_RU["start"], reply_markup=keyboard)


@handlers_router.message(Command(commands=["help", "info"]))
async def process_help_command(message: Message):
    await message.answer(LEXICON_RU["help"], reply_markup=keyboard)


def load_games(filename="games_list.txt"):
    with open(
            filename,
            "r",
            encoding="utf-8"
    ) as file:
        return [
            line.strip()
            for line in file
            if line.strip()
        ]


games_list = load_games()


@handlers_router.inline_query()
async def search_inline(query: InlineQuery):
    text = query.query.strip().lower()

    if not text:
        await query.answer([])
        return

    results = []

    for index, game in enumerate(games_list):

        if text in game.lower():
            results.append(
                InlineQueryResultArticle(
                    id=str(index),
                    title=game,
                    description="PlayStation Store",
                    input_message_content=InputTextMessageContent(
                        message_text=game
                    )
                )
            )

    await query.answer(
        results[:50],
        cache_time=0
    )


@handlers_router.message()
async def send_result(message: Message):
    msg = await message.reply(LEXICON_RU['wait'])

    try:
        prices = await get_prices(message.text)

        await msg.edit_text(
            text=format_prices(prices),
            reply_markup=keyboard
        )

    except Exception:
        logger.exception("Error while getting prices")

        await msg.edit_text(
            LEXICON_RU['error'],
            reply_markup=keyboard
        )
