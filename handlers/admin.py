import asyncio
import logging

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID
from db import (
    get_all_users,
    get_users_count,
    get_warned_users_count,
    get_muted_users_count,
)

router = Router()


async def broadcast_text(bot: Bot, text: str, user_ids: list[int]):
    for uid in user_ids:
        try:
            await bot.send_message(uid, text)
        except Exception as e:
            logging.error(f"Не удалось отправить текст пользователю {uid}: {e}")
        await asyncio.sleep(0.05)


async def broadcast_media(bot: Bot, message: Message, user_ids: list[int]):
    caption = (message.caption or "").removeprefix("/broadcast_media").strip()

    for uid in user_ids:
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
                await bot.send_photo(uid, file_id, caption=caption or None)
            elif message.document:
                file_id = message.document.file_id
                await bot.send_document(uid, file_id, caption=caption or None)
            else:
                continue
        except Exception as e:
            logging.error(f"Не удалось отправить медиа пользователю {uid}: {e}")
        await asyncio.sleep(0.05)


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет прав использовать эту команду.")
        return

    raw_text = message.text or message.caption
    if not raw_text:
        await message.answer("Нет текста для рассылки.")
        return

    text = raw_text.removeprefix("/broadcast").strip()
    if not text:
        await message.answer("Напиши текст после команды: /broadcast текст рекламы")
        return

    users = await get_all_users()

    if not users:
        await message.answer("Пользователей ещё нет.")
        return

    await message.answer(f"Начинаю текстовую рассылку по {len(users)} пользователям...")
    await broadcast_text(bot, text, users)
    await message.answer("Текстовая рассылка завершена.")


@router.message(Command("broadcast_media"))
async def cmd_broadcast_media(message: Message, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет прав использовать эту команду.")
        return

    users = await get_all_users()

    if not users:
        await message.answer("Пользователей ещё нет.")
        return

    if not message.photo and not message.document:
        await message.answer(
            "Прикрепи фото или документ к сообщению с командой:\n"
            "/broadcast_media подпись"
        )
        return

    await message.answer(f"Начинаю медиа-рассылку по {len(users)} пользователям...")
    await broadcast_media(bot, message, users)
    await message.answer("Медиа-рассылка завершена.")


@router.message(Command("show_users"))
@router.message(Command("show_user"))
async def cmd_show_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    users = await get_all_users()

    if not users:
        await message.answer("Пользователей ещё нет.")
        return

    text = "Пользователи:\n" + "\n".join(str(uid) for uid in users)
    await message.answer(text)



@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    users_total = await get_users_count()
    warned = await get_warned_users_count()
    muted = await get_muted_users_count()

    text = (
        "Статистика бота:\n"
        f"👥 Пользователей в БД: {users_total}\n"
        f"⚠ С предупреждениями: {warned}\n"
        f"🔇 Сейчас в муте: {muted}\n"
    )
    await message.answer(text)

