from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message

from handlers.auth import check_subscription


class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]
        user_id = event.from_user.id

        # проверяем подписку КАЖДЫЙ раз
        if not await check_subscription(bot, user_id):
            await event.answer(
                "Чтобы пользоваться ботом, подпишись на канал:\n"
                "https://t.me/focusinghrie\n\n"
                "После подписки нажми /start."
            )
            return  # дальше хендлеры не вызываем

        return await handler(event, data)

