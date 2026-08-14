import json
from urllib.parse import quote

import logging

from .api import (
    API_URL,
    CONCEPT_BY_PRODUCT_HASH,
    MAIN_HEADERS,
    SEARCH_REGION,
)

logger = logging.getLogger(__name__)


COVER_ROLES = (
    "FOUR_BY_THREE_BANNER",
    "EDITION_KEY_ART",
    "PORTRAIT_BANNER",
    "GAMEHUB_COVER_ART",
    "MASTER",
)


def get_cover_url(product: dict) -> str | None:
    media = (
        product
        .get("concept", {})
        .get("media", [])
    )

    for role in COVER_ROLES:
        for item in media:
            if item.get("role") == role:
                return item.get("url")

    return None


async def get_concept_data(
    session,
    product_id,
):
    variables = {
        "productId": product_id,
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": CONCEPT_BY_PRODUCT_HASH,
        }
    }

    url = (
        f"{API_URL}"
        "?operationName=metGetConceptByProductIdQuery"
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

        logger.debug(
            "Concept request status: %s",
            response.status,
        )

        response.raise_for_status()
        data = await response.json()

    try:
        product = data["data"]["productRetrieve"]
        concept = product["concept"]

        return (
            concept["id"],
            get_cover_url(product),
        )

    except (KeyError, TypeError):
        logger.exception(
            "Failed to parse concept data: %s",
            product_id,
        )

        return None, None
