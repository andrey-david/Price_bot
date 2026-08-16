from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from config import Config


class AdminMiddleware(BaseMiddleware):

    def __init__(self, config: Config):
        self.admin_ids = set(config.admin.admin_ids)

    async def __call__(
            self,
            handler,
            event: TelegramObject,
            data: dict,
    ):
        user = data.get("event_from_user")

        if user and user.id in self.admin_ids:
            return await handler(event, data)

        return None
