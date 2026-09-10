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


def format_price_row(
        label: str,
        price: str | None,
        converted_price: float | None,
        user_currency: str,
) -> str:
    if price is None:
        return ""

    converted = (
        f"{converted_price} {user_currency}"
        if converted_price is not None
        else ""
    )

    return f"""
    <tr>
        <td>{label}</td>
        <td align="right">{price}</td>
        <td align="right">{converted}</td>
    </tr>
    """


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

    return format_price_row(
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
    rows = []

    ps_plus_price = data.get(
        "ps_plus_original_price"
    )
    full_price = data.get("price")
    original_price = data.get("original_price")

    # Цена с учётом PS+
    if ps_plus_price is not None:
        rows.append(
            format_price_row(
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
        )

    # Полная цена
    if (
            full_price is not None
            and full_price != ps_plus_price
    ):
        rows.append(
            format_price_row(
                LEXICON[language]["price_full"],
                format_currency_price(
                    full_price,
                    currency_code,
                ),
                data.get("converted_price"),
                user_currency,
            )
        )

    # Обычная цена
    if (
            original_price is not None
            and original_price != ps_plus_price
            and original_price != full_price
    ):
        rows.append(
            format_price_row(
                LEXICON[language]["price_original"],
                format_currency_price(
                    original_price,
                    currency_code,
                ),
                data.get("converted_original_price"),
                user_currency,
            )
        )

    return "".join(rows)


def format_region(
        country: str,
        data: dict,
        user_currency: str,
        language: str,
) -> str:
    if "error" in data:
        return (
            f"<p>"
            f"<b>{country}</b> — "
            f"{data['error']}"
            f"</p>"
        )

    currency_code = data.get(
        "currency_code",
        "",
    )

    caption = f'<a href="{data["url"]}">{country}</a>'

    ps_plus_row = format_ps_plus_price(
        data,
        currency_code,
        language,
        user_currency,
    )

    regular_rows = format_regular_prices(
        data,
        currency_code,
        language,
        user_currency,
    )

    return f"""
    <table bordered striped>
        <caption>{caption}</caption>
        {ps_plus_row}
        {regular_rows}
    </table>
    <hr>
    """


def format_html(
        prices: dict,
        user_currency: str,
        language: str,
) -> str:
    game_name = prices.get(
        "name",
        "Game Name",
    )

    cover_url = prices.get("cover_url")

    cover = (
        f'<img src="{cover_url}"/>'
        if cover_url
        else ""
    )

    regions = "".join(
        format_region(
            country,
            data,
            user_currency,
            language,
        )
        for country, data
        in prices["regions"].items()
    )

    button = f"""
    <tg-button-row align="right">
        <tg-button
            type="switch_inline_query_current_chat"
            style="primary"
        >
            {LEXICON[language]["find a game"]}
        </tg-button>
    </tg-button-row>
    """

    return (
        f'<h2>{game_name}</h2>'
        f'{cover}'
        f'{regions}'
        f'{button}'
    )
