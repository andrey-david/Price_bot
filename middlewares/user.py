from sqlalchemy import select
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database import async_session, User


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler,
            event: TelegramObject,
            data: dict
    ):
        telegram_user = data.get("event_from_user")

        if telegram_user is None:
            return await handler(event, data)

        async with async_session() as session:
            user = await session.scalar(
                select(User)
                .where(User.telegram_id == telegram_user.id)
            )

            data["user"] = user
            data["locale"] = user.language if user else "ru"

        return await handler(event, data)
