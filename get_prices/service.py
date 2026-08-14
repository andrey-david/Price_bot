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
from .format_result import format_prices

logger = logging.getLogger(__name__)


async def get_prices(
    game_name,
    regions,
    user_currency,
):
    async with aiohttp.ClientSession() as session:

        # Поиск игры
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

        # Получаем общий concept ID и одну общую обложку
        concept_id, cover_url = await get_concept_data(
            session,
            product_id,
        )

        if not concept_id:
            logger.warning(
                "Concept ID not found: %s",
                product_id,
            )
            return None

        logger.debug(
            "Concept ID: %s",
            concept_id,
        )

        logger.debug(
            "Cover URL: %s",
            cover_url,
        )

        # Получаем product ID для каждого региона
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

        # Сохраняем только регионы, для которых найден product ID
        regional_data = [
            (region, product_id)
            for region, product_id in zip(
                regions,
                product_ids,
            )
            if product_id
        ]

        # Получаем полную информацию о продуктах
        regional_tasks = [
            get_product(
                session,
                region.ps_locale,
                product_id,
            )
            for region, product_id in regional_data
        ]

        regional_products = await asyncio.gather(
            *regional_tasks
        )

        # Парсим данные всех регионов
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

        # Собираем итоговый словарь
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

        # Формируем текст
        text = format_prices(
            {
                "name": product.get("name"),
                "regions": prices,
            },
            user_currency,
        )

        return cover_url, text
