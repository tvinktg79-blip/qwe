from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from handlers.auth import check_subscription
from handlers.moderation import check_bad_words  # импорт проверки матаfrom typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from handlers.auth import check_subscription
from handlers.moderation import check_bad_words  # импорт проверки мата


class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]
        user_id = event.from_user.id

        # 1) ПЕРВЫЙ: проверяем мат/наркотики ДО подписки
        text_to_check = event.text or event.caption or ""
        if await check_bad_words(text_to_check):
            try:
                await event.delete()
                await bot.send_message(
                    event.chat.id,
                    f"@{event.from_user.username or event.from_user.first_name} "
                    f"({user_id}): сообщение удалено за нарушение правил.",
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")
            return  # дальше не идём

        # 2) ВТОРОЙ: проверяем подписку
        if not await check_subscription(bot, user_id):
            return  # просто режем, без текста

        # 3) если всё ок, запускаем хендлеры
        return await handler(event, data)
