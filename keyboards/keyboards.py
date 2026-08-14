import logging
from functools import wraps

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from lexicon import (
    LEXICON,
    LANGUAGES,
)

logger = logging.getLogger(__name__)


def decorator_add_back_menu_button(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        keyboard = func(*args, **kwargs)

        language = kwargs.get("language")

        if language is None:
            language = args[-1]

        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=LEXICON[language]["back:menu"],
                callback_data="back:menu"
            )
        ])

        return keyboard

    return wrapper


# Menu -----------------------------------------------------------------------
def menu_keyboard(language: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["regions"],
                    callback_data="menu:regions"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["language"],
                    callback_data="menu:language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["currency"],
                    callback_data="menu:currency"
                )
            ],
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["find a game"],
                    switch_inline_query_current_chat="",
                    style="primary"
                )
            ]
        ]
    )


# Find game -----------------------------------------------------------------------
def find_game_keyboard(language: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["find a game"],
                    switch_inline_query_current_chat="",
                    style="primary"
                )
            ],

        ]
    )


# Region -----------------------------------------------------------------------
def _regions_keyboard(
        regions,
        selected_regions=None,
        language: str = "en",
        start: bool = False,
):
    if selected_regions is None:
        selected_regions = set()

    keyboard = []
    row = []
    REGION_GROUPS = LEXICON[language]["REGION_GROUPS"]

    prefix = "start_region" if start else "region"

    for region in regions:
        if region.country in REGION_GROUPS:
            if row:
                keyboard.append(row)
                row = []

            keyboard.append([
                InlineKeyboardButton(
                    text=f"{REGION_GROUPS[region.country]}",
                    callback_data="separator",
                    style="danger"
                )
            ])

        mark = "✅ " if region.id in selected_regions else ""

        row.append(
            InlineKeyboardButton(
                text=f"{mark}{region.country}",
                callback_data=f"{prefix}:{region.id}"
            )
        )

        if len(row) == 3:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return keyboard


@decorator_add_back_menu_button
def regions_keyboard(
        regions,
        selected_regions=None,
        language="en"
):
    keyboard = _regions_keyboard(
        regions,
        selected_regions,
        language
    )

    keyboard.append([
        InlineKeyboardButton(
            text=LEXICON[language]["find a game"],
            switch_inline_query_current_chat="",
            style="primary"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def regions_keyboard_no_back(
        regions,
        selected_regions=None,
        language="en"
):
    return InlineKeyboardMarkup(
        inline_keyboard=_regions_keyboard(
            regions,
            selected_regions,
            language
        )
    )


def regions_keyboard_on_start(
        language="en"
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LEXICON[language]["regions"],
                    callback_data=f"start_region",
                )
            ],

        ]
    )


# Language -----------------------------------------------------------------------
def _languages_keyboard(
        start: bool = False,
):
    keyboard = []

    prefix = "start_language" if start else "language"

    for code, name in LANGUAGES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"{prefix}:{code}"
            )
        ])

    return keyboard


@decorator_add_back_menu_button
def languages_keyboard(
        language: str = "en",
):
    return InlineKeyboardMarkup(
        inline_keyboard=_languages_keyboard()
    )


def languages_keyboard_on_start(
        language: str = "en",
):
    return InlineKeyboardMarkup(
        inline_keyboard=_languages_keyboard(start=True)
    )


# Currency -----------------------------------------------------------------------
def _currency_keyboard(
        currencies: dict[str, str],
        selected_currency: str | None = None,
        start: bool = False,
):
    keyboard = []
    row = []

    prefix = "start_currency" if start else "currency"

    for code, name in currencies.items():
        mark = "✅ " if code == selected_currency else ""

        row.append(
            InlineKeyboardButton(
                text=f"{mark}{name}",
                callback_data=f"{prefix}:{code}"
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return keyboard


@decorator_add_back_menu_button
def currency_keyboard(
        currencies: dict[str, str],
        selected_currency: str | None,
        language: str = "en",
):
    return InlineKeyboardMarkup(
        inline_keyboard=_currency_keyboard(
            currencies,
            selected_currency,
            start=False,
        )
    )


def currency_keyboard_on_start(
        currencies: dict[str, str],
        language: str = "en",
):
    return InlineKeyboardMarkup(
        inline_keyboard=_currency_keyboard(
            currencies,
            start=True,
        )
    )
