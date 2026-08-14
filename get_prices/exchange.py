import logging

import aiohttp

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = aiohttp.ClientTimeout(total=10)

async def fetch_as_json(
        session: aiohttp.ClientSession,
        url: str,
        headers: dict | None = None,
) -> dict:
    """Sends a GET request and returns the response as JSON."""
    async with session.get(
            url,
            headers=headers,
            timeout=HTTP_TIMEOUT,
    ) as response:
        text = await response.text()

        response.raise_for_status()

        return await response.json()


async def get_exchange_rate(
        session: aiohttp.ClientSession,
        from_currency: str,
        to_currency: str,
) -> float:
    """Returns the exchange rate from one currency to another."""
    if from_currency == to_currency:
        return 1.0

    url = (
        "https://api.exchangerate-api.com/v4/latest/"
        f"{from_currency}"
    )

    data = await fetch_as_json(session, url)

    return data["rates"][to_currency]
