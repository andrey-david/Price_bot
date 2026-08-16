import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import (
    Config,
    load_config,
)
from handlers import (
    handlers_router,
    handlers_region_router,
    handlers_gamefider,
    handlers_language,
    admin_router,
)
from keyboards import (
    set_main_menu,
)
from database import (
    init_db
)
from middlewares import (
    UserMiddleware,
    AdminMiddleware,
)

logger = logging.getLogger(__name__)


async def main():
    # Config
    config: Config = load_config()

    # Logging
    log_path = 'bot.log'
    logging_handler = logging.FileHandler(filename=log_path, encoding='utf-8')
    logging_console = logging.StreamHandler()
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
        style='{',
        handlers=[logging_handler, logging_console],
        encoding='utf-8'
    )

    logger.info(f"BOT JUST STARTED")

    # Initialising bot
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    admin_router.message.middleware(AdminMiddleware(config))
    dp.include_router(admin_router)

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.inline_query.middleware(UserMiddleware())

    dp.startup.register(set_main_menu)

    dp.include_router(handlers_router)
    dp.include_router(handlers_region_router)
    dp.include_router(handlers_gamefider)
    dp.include_router(handlers_language)

    # Initialising db
    await init_db()

    # Start pulling
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
