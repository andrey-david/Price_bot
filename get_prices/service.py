import asyncio
import logging

import aiohttp

from .search import search_game
from .concept import get_concept_data
from .product import (
    get_product_id,
    get_product,
)
from .parser import parse_product
from .format_result import format_html

logger = logging.getLogger(__name__)


async def find_product(session, game_name):
    product = await search_game(
        session,
        game_name,
    )

    if product is None:
        logger.warning(
            "Game not found: %s",
            game_name,
        )
        return None

    product_id = product.get("id")

    if not product_id:
        logger.warning(
            "Product ID not found: %s",
            game_name,
        )
        return None

    logger.info(
        "Game found: %s",
        product.get("name"),
    )

    return product


async def get_regional_product_ids(
        session,
        concept_id,
        regions,
):
    product_tasks = [
        get_product_id(
            session,
            concept_id,
            region.ps_locale,
        )
        for region in regions
    ]

    product_ids = await asyncio.gather(
        *product_tasks
    )

    logger.debug(
        "Regional product IDs: %s",
        product_ids,
    )

    return [
        (region, product_id)
        for region, product_id in zip(
            regions,
            product_ids,
        )
        if product_id
    ]


async def get_regional_products(
        session,
        regional_data,
):
    regional_tasks = [
        get_product(
            session,
            region.ps_locale,
            product_id,
        )
        for region, product_id in regional_data
    ]

    return await asyncio.gather(
        *regional_tasks
    )


async def parse_regional_products(
        session,
        regional_data,
        regional_products,
        user_currency,
):
    parse_tasks = [
        parse_product(
            product_data,
            region,
            session,
            user_currency,
        )
        for (region, _), product_data in zip(
            regional_data,
            regional_products,
        )
    ]

    parsed_products = await asyncio.gather(
        *parse_tasks
    )

    prices = {
        region.country: data
        for (region, _), data in zip(
            regional_data,
            parsed_products,
        )
    }

    logger.debug(
        "Parsed prices: %s",
        prices,
    )

    return prices


async def html_message(
        game_name,
        regions,
        user_currency,
        user_language,
):
    async with aiohttp.ClientSession() as session:

        # Поиск игры
        product = await find_product(
            session,
            game_name,
        )

        if product is None:
            return None

        # Получаем общий concept ID и одну общую обложку
        concept_id, cover_url = await get_concept_data(
            session,
            product["id"],
        )

        if not concept_id:
            return None

        # Получаем product ID для каждого региона
        regional_data = await get_regional_product_ids(
            session,
            concept_id,
            regions,
        )

        # Получаем полную информацию о продуктах
        regional_products = await get_regional_products(
            session,
            regional_data,
        )

        # Парсим данные всех регионов
        prices = await parse_regional_products(
            session,
            regional_data,
            regional_products,
            user_currency,
        )

        # Формируем текст
        html = format_html(
            {
                "name": product.get("name"),
                "cover_url": cover_url,
                "regions": prices,
            },
            user_currency,
            user_language,
        )

        return html
