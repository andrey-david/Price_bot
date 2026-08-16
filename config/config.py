import logging
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)


@dataclass
class TgBot:
    token: str


@dataclass
class LogSettings:
    level: str
    format: str


@dataclass
class Config:
    bot: TgBot
    log: LogSettings
    admin: Admin


@dataclass
class Admin:
    admin_ids: list[int]


def load_config(path: str | None = None) -> Config:
    env = Env()
    path = '.env'
    env.read_env(path)

    return Config(
        bot=TgBot(token=env("BOT_TOKEN")),
        log=LogSettings(level=env("LOG_LEVEL"), format=env("LOG_FORMAT")),
        admin=Admin(admin_ids=list(map(int, env.list('ADMIN_IDS')))),
    )
