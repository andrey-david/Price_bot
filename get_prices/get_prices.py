import asyncio
import logging
import re
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0"
}


async def fetch(session, url):
    async with session.get(
        url,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as response:
        response.raise_for_status()
        return await response.text()


async def fetch_json(session, url):
    async with session.get(
        url,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as response:
        response.raise_for_status()
        return await response.json()


def get_number(price, currency):
    if not price:
        return None

    number = re.sub(r"[^\d.,]", "", price)

    if currency in ("EUR", "BRL", "TRY"):
        number = number.replace(".", "")
        number = number.replace(",", ".")

    elif currency in ("JPY", "INR"):
        number = number.replace(",", "")

    else:
        number = number.replace(",", "")

    return float(number)


async def convert_currency(session, amount, from_currency, to_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    data = await fetch_json(session, url)
    rate = data["rates"][to_currency]
    return round(amount * rate, 2)


async def search_game(session, game_name, region):
    url = (
        f"https://store.playstation.com/"
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
        f"https://store.playstation.com/"
        f"{region}/product/{product_id}"
    )


async def get_game_info(session, url):
    html = await fetch(session, url)

    soup = BeautifulSoup(html, "lxml")

    name = soup.find(
        "h1",
        {"data-qa": "mfe-game-title#name"}
    )

    price = re.search(
        r'"priceOrText":"([^"]+)"',
        html
    )

    old_price = re.search(
        r'"originalPrice":"([^"]+)"',
        html
    )

    return {
        "name": name.text.strip() if name else None,
        "price": price.group(1) if price else None,
        "original_price": old_price.group(1) if old_price else None,
    }


async def get_region_price(
    session,
    country,
    data,
    game_name,
    user_currency
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

    info["url"] = url
    info["currency"] = currency

    amount = get_number(
        info["original_price"],
        currency
    )

    if amount is not None:
        info["converted_price"] = await convert_currency(
            session,
            amount,
            currency,
            user_currency
        )
    else:
        info["converted_price"] = None

    return country, info

async def get_prices(game_name, regions, user_currency):
    async with aiohttp.ClientSession() as session:

        tasks = [
            get_region_price(
                session,
                region.country,
                {
                    "region": region.ps_locale,
                    "currency": region.currency
                },
                game_name,
                user_currency
            )
            for region in regions
        ]

        results = await asyncio.gather(*tasks)

    return dict(results)


def format_prices(prices, user_currency):
    game_name = next(
        (
            data["name"]
            for data in prices.values()
            if "name" in data
        ),
        "Игра"
    )

    text = f"🎮 <b>{game_name}</b>\n"
    text += "🌍 <b>Цены по регионам:</b>\n\n"

    for country, data in prices.items():

        if "error" in data:
            text += (
                f"{country} — {data['error']}\n\n"
            )
            continue

        text += (
            f"{country} | "
            f"<a href='{data['url']}'>{data['name']}</a>\n"
            f"    Цена с PS+: {data['price']}\n"
            f"    Цена: {data['original_price']} "
            f"≈ <b>{data['converted_price']} {user_currency}</b>\n\n"
        )

    return text
