import logging

from lexicon import LEXICON

logger = logging.getLogger(__name__)


def format_currency_price(
        price: float,
        currency_code: str,
) -> str:
    if price.is_integer():
        return f"{int(price)} {currency_code}"

    return f"{price:.2f} {currency_code}"


def format_price(
        label: str,
        price: str | None,
        converted_price: float | None,
        currency: str,
) -> str:
    if price is None:
        return ""

    converted = (
        f"{converted_price} {currency}"
        if converted_price is not None
        else ""
    )

    return (
        f"<code> {label:<6} "
        f"{price:<9} "
        f"{converted:<9}</code>\n"
    )


def format_ps_plus_price(
        data: dict,
        currency_code: str,
        language: str,
        user_currency: str,
) -> str:
    price = data.get("ps_plus_price")

    if price is None:
        display_price = None
    elif price == 0:
        display_price = LEXICON[language]["included"]
    else:
        display_price = format_currency_price(
            price,
            currency_code,
        )

    return format_price(
        LEXICON[language]["ps+"],
        display_price,
        None,
        user_currency,
    )


def format_regular_prices(
        data: dict,
        currency_code: str,
        language: str,
        user_currency: str,
) -> str:
    text = ""

    ps_plus_price = data.get("ps_plus_original_price")
    full_price = data.get("price")
    original_price = data.get("original_price")

    # Цена с учётом PS+
    if ps_plus_price is not None:
        text += format_price(
            LEXICON[language]["price_ps+"],
            format_currency_price(
                ps_plus_price,
                currency_code,
            ),
            data.get(
                "converted_ps_plus_original_price"
            ),
            user_currency,
        )

    # Полная цена
    if full_price is not None and full_price != ps_plus_price:
        text += format_price(
            LEXICON[language]["price_full"],
            format_currency_price(
                full_price,
                currency_code,
            ),
            data.get("converted_price"),
            user_currency,
        )

    # Обычная цена
    if (
            original_price is not None
            and original_price != ps_plus_price
            and original_price != full_price
    ):
        text += format_price(
            LEXICON[language]["price_original"],
            format_currency_price(
                original_price,
                currency_code,
            ),
            data.get("converted_original_price"),
            user_currency,
        )

    return text


def format_region(
        country: str,
        data: dict,
        user_currency: str,
        language: str,
) -> str:
    if "error" in data:
        return (
            f"{country} — "
            f"{data['error']}\n\n"
        )

    currency_code = data.get(
        "currency_code",
        "",
    )

    text = (
        f"<a href='{data['url']}'>"
        f"{country}"
        f"</a>\n"
    )

    text += format_ps_plus_price(
        data,
        currency_code,
        language,
        user_currency,
    )

    text += format_regular_prices(
        data,
        currency_code,
        language,
        user_currency,
    )

    return text + "\n"


def format_prices(
        prices: dict,
        user_currency: str,
        language: str,
) -> str:
    game_name = prices.get(
        "name",
        "Game Name",
    )

    text = (
        f"🎮 <b>{game_name}</b>\n\n"
    )

    for country, data in prices["regions"].items():
        text += format_region(
            country,
            data,
            user_currency,
            language,
        )

    return text
