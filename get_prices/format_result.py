import logging

logger = logging.getLogger(__name__)


def format_currency_price(
        price: float,
        currency_code: str,
) -> str:
    if price.is_integer():
        return f"{int(price)} {currency_code}"

    return f"{price:.2f} {currency_code}"


def format_price(
        label,
        price,
        converted_price,
        currency,
):
    if price is None:
        return ""

    converted = (
        f"{converted_price} {currency}"
        if converted_price is not None
        else ""
    )

    return (
        f"<code> {label:<8} "
        f"{price:<10} "
        f"{converted:<10}</code>\n"
    )


def format_prices(
        prices,
        user_currency,
):
    game_name = prices.get(
        "name",
        "Game Name",
    )

    text = (
        f"🎮 <b>{game_name}</b>\n\n"
    )

    for country, data in prices["regions"].items():

        if "error" in data:
            text += (
                f"{country} — "
                f"{data['error']}\n\n"
            )
            continue

        currency_code = data.get(
            "currency_code",
            "",
        )

        text += (
            f"<a href='{data['url']}'>"
            f"{country}"
            f"</a>\n"
        )

        # PS+
        ps_plus_price = data.get(
            "ps_plus_price"
        )

        if ps_plus_price is None:
            ps_plus_display = None
        elif ps_plus_price == 0:
            ps_plus_display = "Included"
        else:
            ps_plus_display = format_currency_price(
                ps_plus_price,
                currency_code,
            )

        text += format_price(
            "PS+",
            ps_plus_display,
            None,
            user_currency,
        )

        # Цена для PS+
        ps_plus_original_price = data.get(
            "ps_plus_original_price"
        )

        if ps_plus_original_price is not None:
            ps_plus_original_price = (
                format_currency_price(
                    ps_plus_original_price,
                    currency_code,
                )
            )

        text += format_price(
            "Цена",
            ps_plus_original_price,
            data.get(
                "converted_ps_plus_original_price"
            ),
            user_currency,
        )

        # Цена для PS+
        ps_plus_original_price = data.get(
            "ps_plus_original_price"
        )

        if ps_plus_original_price is not None:
            ps_plus_display = format_currency_price(
                ps_plus_original_price,
                currency_code,
            )

            text += format_price(
                "Цена",
                ps_plus_display,
                data.get("converted_ps_plus_original_price"),
                user_currency,
            )

        # Полная цена
        price = data.get("price")

        if (
                price is not None
                and price != ps_plus_original_price
        ):
            price_display = format_currency_price(
                price,
                currency_code,
            )

            text += format_price(
                "Полная",
                price_display,
                data.get("converted_price"),
                user_currency,
            )

        # Обычная цена
        original_price = data.get("original_price")

        if (
                original_price is not None
                and original_price != ps_plus_original_price
                and original_price != price
        ):
            original_price_display = format_currency_price(
                original_price,
                currency_code,
            )

            text += format_price(
                "Обычная",
                original_price_display,
                data.get("converted_original_price"),
                user_currency,
            )

        text += "\n"

    return text
