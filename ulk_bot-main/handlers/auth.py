import logging

from aiogram import Router, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from db import add_user  # ← только это

router = Router()

CHANNEL_USERNAME = "@focusinghrie"  # твой канал

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")],
    ],
    resize_keyboard=True
)


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет подписку БЕЗ отправки текста"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False  # нет доступа или не подписан



@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    # сохраняем пользователя в БД
    await add_user(message.from_user.id)


    if not await check_subscription(bot, message.from_user.id):
        await message.answer(
            "Чтобы пользоваться ботом, подпишись на канал:\n"
            "https://t.me/focusinghrie"
        )
        await message.answer(
            "После подписки нажми кнопку /start ниже 👇",
            reply_markup=start_kb
        )
        return

    from handlers.schedule import courses_kb

    await message.answer(
        "Привет, я бот УЛК по расписанию.\n"
        "Выбери курс:",
        reply_markup=courses_kb
    )

