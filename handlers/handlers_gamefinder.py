import logging

from aiogram import Router
from aiogram.types import (
    Message,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from get_prices import (
    get_prices,
    format_prices,
)
from lexicon import (
    LEXICON,
)
from keyboards import (
    find_game_keyboard,
)
from database import (
    User,
)

logger = logging.getLogger(__name__)
handlers_gamefider = Router(name='handlers_gamefider')


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


@handlers_gamefider.inline_query()
async def search_inline(
    query: InlineQuery,
    user: User
):
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
                    description=LEXICON[user.language]["inline_description"],
                    input_message_content=InputTextMessageContent(
                        message_text=game
                    )
                )
            )

    await query.answer(
        results[:50],
        cache_time=0
    )


@handlers_gamefider.message()
async def send_result(
        message: Message,
        user: User
):
    msg = await message.reply(
        LEXICON[user.language]["wait"]
    )

    try:
        regions = user.regions

        if not regions:
            await msg.edit_text(
                LEXICON[user.language]["no_region"]
            )
            return

        user_currency = user.currency

        prices = await get_prices(
            message.text,
            regions,
            user_currency
        )

        await msg.edit_text(
            text=format_prices(
                prices,
                user_currency
            ),
            reply_markup=find_game_keyboard(language=user.language),
            disable_web_page_preview=True,
        )

    except Exception:
        logger.exception("Error while getting prices")

        await msg.edit_text(
            LEXICON[user.language]["error"],
            reply_markup=find_game_keyboard(language=user.language)
        )
