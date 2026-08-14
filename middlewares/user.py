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
                select(User).where(
                    User.telegram_id == event.from_user.id
                )
            )

            if user is None:
                user = User(
                    telegram_id=event.from_user.id,
                    username=event.from_user.username,
                    first_name=event.from_user.first_name,
                    language="ru",
                    currency="USD",
                )

                session.add(user)
                await session.commit()

            data["user"] = user
            data["language"] = user.language

        return await handler(event, data)
