import logging

from .exchange import get_exchange_rate

logger = logging.getLogger(__name__)

NO_DIVIDE_CURRENCIES = {
    "INR",
    "JPY",
    "KRW",
    "IDR",
}


def normalize_price(
        value: int | float,
        currency: str,
) -> float:
    divisor = 1 if currency in NO_DIVIDE_CURRENCIES else 100
    return value / divisor


def get_price(
        price: dict | None,
) -> dict | None:
    if not price:
        return None

    currency = price.get("currencyCode")

    return {
        "currency": currency,
        "base_price": normalize_price(
            price.get("basePriceValue", 0),
            currency,
        ),
        "price": normalize_price(
            price.get("discountedValue", 0),
            currency,
        ),
        "discount": price.get("discountText"),
        "is_free": price.get("isFree"),
        "ps_plus": price.get("isTiedToSubscription"),
    }


def get_ps_plus_prices(
        ctas: list[dict],
) -> list[dict]:
    result = []

    for cta in ctas:
        price = cta.get("price")

        if not price:
            continue

        if not price.get("isTiedToSubscription"):
            continue

        currency = price.get("currencyCode")

        result.append({
            "type": cta.get("type"),
            "currency": currency,
            "price": normalize_price(
                price.get("discountedValue", 0),
                currency,
            ),
            "base_price": normalize_price(
                price.get("basePriceValue", 0),
                currency,
            ),
            "subscription": price.get(
                "serviceBranding",
            ),
            "text": price.get(
                "upsellText",
            ),
            "included": (
                price.get("discountedPrice")
                == "Included"
            ),
        })

    return result


async def parse_product(
        product,
        region,
        session,
        user_currency,
):
    product_data = product["data"]["productRetrieve"]

    price_data = get_price(
        product_data.get("price")
    )

    ps_plus_prices = get_ps_plus_prices(
        product_data.get("mobilectas", [])
    )

    ps_plus = (
        ps_plus_prices[0]
        if ps_plus_prices
        else None
    )

    currency_code = (
        price_data["currency"]
        if price_data
        else None
    )

    rate = await get_exchange_rate(
        session,
        currency_code,
        user_currency,
    )

    return {
        "url": (
            f"https://store.playstation.com/"
            f"{region.ps_locale}/product/"
            f"{product_data.get('id')}"
        ),

        "currency_code": currency_code,

        "price": (
            price_data["price"]
            if price_data
            else None
        ),

        "original_price": (
            price_data["base_price"]
            if price_data
            else None
        ),

        "ps_plus_price": (
            ps_plus["price"]
            if ps_plus
            else None
        ),

        "ps_plus_original_price": (
            ps_plus["base_price"]
            if ps_plus
            else None
        ),

        "converted_price": (
            round(
                price_data["price"] * rate,
                2,
            )
            if price_data
            else None
        ),

        "converted_original_price": (
            round(
                price_data["base_price"] * rate,
                2,
            )
            if price_data
            else None
        ),

        "converted_ps_plus_original_price": (
            round(
                ps_plus["base_price"] * rate,
                2,
            )
            if ps_plus
            else None
        ),
    }
