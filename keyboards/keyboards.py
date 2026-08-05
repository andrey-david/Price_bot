import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lexicon import LEXICON_RU

logger = logging.getLogger(__name__)

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=LEXICON_RU['find a game'],
                switch_inline_query_current_chat=""
            )
        ]
    ]
)
