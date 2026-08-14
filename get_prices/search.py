import json
from urllib.parse import quote
import logging

from .api import (
    API_URL,
    MAIN_HEADERS,
    SEARCH_HASH,
    SEARCH_REGION,
)

logger = logging.getLogger(__name__)


async def search_game(session, game_name):
    language_code, country_code = SEARCH_REGION.split("-")

    variables = {
        "countryCode": country_code.upper(),
        "languageCode": language_code,
        "nextCursor": "",
        "pageOffset": 0,
        "pageSize": 24,
        "searchTerm": game_name.lower(),
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": SEARCH_HASH,
        }
    }

    url = (
        f"{API_URL}"
        "?operationName=getSearchResults"
        f"&variables={quote(json.dumps(variables, separators=(',', ':')))}"
        f"&extensions={quote(json.dumps(extensions, separators=(',', ':')))}"
    )

    headers = {
        **MAIN_HEADERS,
        "x-psn-store-locale-override": SEARCH_REGION,
    }

    async with session.get(
            url,
            headers=headers,
            timeout=10,
    ) as response:
        response.raise_for_status()
        data = await response.json()

    products = data["data"]["universalSearch"]["results"]

    target_name = game_name.casefold().strip()

    for product in products:
        name = product.get(
            "name",
            "",
        ).casefold().strip()

        classification = (
            product.get(
                "localizedStoreDisplayClassification",
                "",
            )
            .casefold()
            .strip()
        )

        if (
                name == target_name
                and classification == "full game"
        ):
            return product

    for product in products:
        if (
                product.get(
                    "name",
                    "",
                ).casefold().strip()
                == target_name
        ):
            return product

    return products[0] if products else None
