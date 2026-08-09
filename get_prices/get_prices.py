import asyncio
import logging
import re
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

HTTP_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def fetch(session, url):
    async with session.get(
        url,
        headers=HEADERS,
        timeout=HTTP_TIMEOUT
    ) as response:
        response.raise_for_status()
        return await response.text()


async def fetch_json(session, url):
    async with session.get(
        url,
        timeout=HTTP_TIMEOUT
    ) as response:
        response.raise_for_status()
        return await response.json()


def get_number(price, currency):
    if not price:
        return None

    number = re.sub(r"[^\d.,\s]", "", price)
    number = number.strip()

    if not number:
        return None

    # Пробелы используются как разделитель тысяч:
    # UAH 2 299,00 -> 2299,00
    number = number.replace(" ", "")

    if "," in number and "." in number:
        # Например: 1.299,99
        if number.rfind(",") > number.rfind("."):
            number = number.replace(".", "")
            number = number.replace(",", ".")
        # Например: 1,299.99
        else:
            number = number.replace(",", "")

    elif "," in number:
        # Для валют с запятой как десятичным разделителем
        number = number.replace(",", ".")

    elif "." in number:
        # Если точка используется как разделитель тысяч
        parts = number.split(".")

        if currency in ("EUR", "BRL", "TRY", "UAH"):
            if len(parts) > 1 and len(parts[-1]) == 2:
                # 2299.99
                pass
            else:
                # 2.299 -> 2299
                number = number.replace(".", "")

    try:
        return float(number)
    except ValueError:
        return None


async def get_exchange_rate(
    session,
    from_currency,
    to_currency
):
    if from_currency == to_currency:
        return 1

    url = (
        "https://api.exchangerate-api.com/v4/latest/"
        f"{from_currency}"
    )

    data = await fetch_json(session, url)

    return data["rates"][to_currency]


async def search_game(
    session,
    game_name,
    region
):
    url = (
        "https://store.playstation.com/"
        f"{region}/search/{quote(game_name)}"
    )

    html = await fetch(session, url)

    match = re.search(
        rf'"/{region}/product/([^"]+)"',
        html
    )

    if not match:
        return None

    product_id = match.group(1)

    return (
        "https://store.playstation.com/"
        f"{region}/product/{product_id}"
    )


async def get_game_info(session, url):
    html = await fetch(session, url)

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    name = soup.find(
        "h1",
        {"data-qa": "mfe-game-title#name"}
    )

    offers = []

    for offer in range(10):
        final_price = soup.find(
            "span",
            {
                "data-qa":
                f"mfeCtaMain#offer{offer}#finalPrice"
            }
        )

        if final_price is None:
            continue

        original_price = soup.find(
            "span",
            {
                "data-qa":
                f"mfeCtaMain#offer{offer}#originalPrice"
            }
        )

        ps_plus_icon = soup.find(
            "span",
            {
                "data-qa":
                f"mfeCtaMain#offer{offer}#serviceIcon#ps-plus"
            }
        )

        offers.append({
            "final_price": final_price.get_text(
                strip=True
            ),
            "original_price": (
                original_price.get_text(strip=True)
                if original_price
                else None
            ),
            "ps_plus": ps_plus_icon is not None,
        })

    return {
        "name": (
            name.get_text(strip=True)
            if name
            else None
        ),
        "offers": offers,
    }


async def get_region_price(
    session,
    country,
    data,
    game_name,
    exchange_rates
):
    region = data["region"]
    currency = data["currency"]

    logger.debug(f"Checking {country}")

    url = await search_game(
        session,
        game_name,
        region
    )

    if not url:
        return country, {
            "error": "Not found"
        }

    info = await get_game_info(
        session,
        url
    )

    offers = info["offers"]

    ps_plus_price = None
    ps_plus_original_price = None

    price = None
    original_price = None

    # Ищем PS+ предложение
    for offer in offers:
        if offer["ps_plus"]:
            ps_plus_price = offer["final_price"]
            ps_plus_original_price = offer["original_price"]
            break

    # Ищем обычное предложение
    for offer in offers:
        if not offer["ps_plus"]:
            price = offer["final_price"]
            original_price = offer["original_price"]
            break

    rate = exchange_rates[currency]

    # Цена обычной покупки
    converted_price = None

    if price:
        amount = get_number(
            price,
            currency
        )

        if amount is not None:
            converted_price = round(
                amount * rate,
                2
            )

    # Оригинальная цена PS+ предложения
    converted_ps_plus_original_price = None

    if ps_plus_original_price:
        amount = get_number(
            ps_plus_original_price,
            currency
        )

        if amount is not None:
            converted_ps_plus_original_price = round(
                amount * rate,
                2
            )

    # Оригинальная цена обычного предложения
    converted_original_price = None

    if original_price:
        amount = get_number(
            original_price,
            currency
        )

        if amount is not None:
            converted_original_price = round(
                amount * rate,
                2
            )

    return country, {
        "name": info["name"],
        "url": url,
        "currency": currency,

        "ps_plus_price": ps_plus_price,
        "ps_plus_original_price": ps_plus_original_price,
        "converted_ps_plus_original_price":
            converted_ps_plus_original_price,

        "price": price,
        "original_price": original_price,
        "converted_price": converted_price,
        "converted_original_price":
            converted_original_price,
    }


async def get_prices(
    game_name,
    regions,
    user_currency
):
    async with aiohttp.ClientSession() as session:

        currencies = {
            region.currency
            for region in regions
        }

        rate_tasks = {
            currency: get_exchange_rate(
                session,
                currency,
                user_currency
            )
            for currency in currencies
        }

        rates = await asyncio.gather(
            *rate_tasks.values()
        )

        exchange_rates = dict(
            zip(
                rate_tasks.keys(),
                rates
            )
        )

        tasks = [
            get_region_price(
                session,
                region.country,
                {
                    "region": region.ps_locale,
                    "currency": region.currency
                },
                game_name,
                exchange_rates
            )
            for region in regions
        ]

        results = await asyncio.gather(
            *tasks
        )

    return dict(results)


def format_prices(
    prices,
    user_currency
):
    game_name = next(
        (
            data["name"]
            for data in prices.values()
            if "name" in data
        ),
        "Игра"
    )

    text = (
        f"🎮 <b>{game_name}</b>\n"
        "🌍 <b>Цены по регионам:</b>\n\n"
    )

    for country, data in prices.items():

        if "error" in data:
            text += (
                f"{country} — "
                f"{data['error']}\n\n"
            )
            continue

        text += (
            f"{country} | "
            f"<a href='{data['url']}'>"
            f"{data['name']}</a>\n"
        )

        # PS+
        if data["ps_plus_price"]:
            text += (
                f"    Цена с PS+: "
                f"{data['ps_plus_price']}\n"
            )

            if data["ps_plus_original_price"]:
                text += (
                    f"    Обычная цена: "
                    f"{data['ps_plus_original_price']}"
                )

                if (
                    data[
                        "converted_ps_plus_original_price"
                    ]
                    is not None
                ):
                    text += (
                        f" ≈ <b>"
                        f"{data['converted_ps_plus_original_price']} "
                        f"{user_currency}"
                        f"</b>"
                    )

                text += "\n"

        # Обычная покупка
        if data["price"]:
            text += (
                f"    Цена: "
                f"{data['price']}"
            )

            if data["converted_price"] is not None:
                text += (
                    f" ≈ <b>"
                    f"{data['converted_price']} "
                    f"{user_currency}"
                    f"</b>"
                )

            text += "\n"

        # Старая цена обычной покупки
        if (
            data["original_price"]
            and data["original_price"] != data["ps_plus_original_price"]
        ):
            text += (
                f"    Обычная цена: "
                f"{data['original_price']}"
            )

            if data["converted_original_price"] is not None:
                text += (
                    f" ≈ <b>"
                    f"{data['converted_original_price']} "
                    f"{user_currency}"
                    f"</b>"
                )

            text += "\n"

        text += "\n"

    return text
