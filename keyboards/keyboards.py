import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lexicon import (
    LEXICON,
    LANGUAGES,
)

logger = logging.getLogger(__name__)


def find_game_keyboard(language: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["regions"],
                    callback_data="settings:regions"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["find a game"],
                    switch_inline_query_current_chat=""
                )
            ],

        ]
    )


def settings_keyboard(language: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["regions"],
                    callback_data="settings:regions"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["language"],
                    callback_data="settings:language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["currency"],
                    callback_data="settings:currency"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["find a game"],
                    switch_inline_query_current_chat=""
                )
            ]
        ]
    )


def regions_keyboard(
        regions,
        selected_regions=None,
        language="ru"
):
    if selected_regions is None:
        selected_regions = set()

    keyboard = []
    row = []

    for region in regions:
        mark = "✅ " if region.id in selected_regions else ""

        row.append(
            InlineKeyboardButton(
                text=f"{mark}{region.country}",
                callback_data=f"region:{region.id}"
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(
                text=LEXICON[language]["back:settings"],
                callback_data="back:settings"
            )
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                text=LEXICON[language]["find a game"],
                switch_inline_query_current_chat=""
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def languages_keyboard(language: str):
    keyboard = []

    for code, name in LANGUAGES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"language:{code}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text=LEXICON[language]["back:settings"],
            callback_data="back:settings"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def languages_keyboard_on_start(language: str):
    keyboard = []

    for code, name in LANGUAGES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"language:{code}"
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def currency_keyboard(
        currencies: dict[str, str],
        selected_currency: str | None = None,
        language: str = "ru"
):
    keyboard = []
    row = []

    for code, name in currencies.items():
        mark = "✅ " if code == selected_currency else ""

        row.append(
            InlineKeyboardButton(
                text=f"{mark}{name}",
                callback_data=f"currency:{code}"
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(
            text=LEXICON[language]["back:settings"],
            callback_data="back:settings"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )
