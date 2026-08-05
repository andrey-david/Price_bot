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
)
from keyboards import (
    set_main_menu,
)

logger = logging.getLogger(__name__)


def main():
    config: Config = load_config()

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

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.startup.register(set_main_menu)
    dp.include_router(handlers_router)
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
