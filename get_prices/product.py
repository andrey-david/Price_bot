import json
from urllib.parse import quote
import logging

from .api import (
    API_URL,
    CONCEPT_BY_ID_HASH,
    CONCEPT_BY_PRODUCT_HASH,
    MAIN_HEADERS,
)

logger = logging.getLogger(__name__)


async def get_product_id(
    session,
    concept_id,
    region,
):
    variables = {
        "conceptId": concept_id,
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": CONCEPT_BY_ID_HASH,
        }
    }

    url = (
        f"{API_URL}"
        "?operationName=metGetConceptById"
        f"&variables={quote(json.dumps(variables, separators=(',', ':')))}"
        f"&extensions={quote(json.dumps(extensions, separators=(',', ':')))}"
    )

    headers = {
        **MAIN_HEADERS,
        "x-psn-store-locale-override": region,
    }

    async with session.get(
        url,
        headers=headers,
        timeout=15,
    ) as response:

        if response.status != 200:
            logger.debug(
                "%s: HTTP %s",
                region.upper(),
                response.status,
            )
            return None

        data = await response.json()

    try:
        return (
            data["data"]
            ["conceptRetrieve"]
            ["defaultProduct"]
            ["id"]
        )

    except (KeyError, TypeError):
        logger.debug(
            "Product ID not found: %s",
            region,
        )
        return None


async def get_product(
    session,
    region,
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
        "x-psn-store-locale-override": region,
    }

    async with session.get(
        url,
        headers=headers,
        timeout=15,
    ) as response:

        response.raise_for_status()
        return await response.json()
