from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_helper import db_helper
from app.models.models import User, Chat

from app.crud.user import read_user, create_user
from app.crud.chat import read_chat, create_chat

from app.core.config import settings
from aiohttp import ClientSession


onboarding_router = Router()

async def is_user_in_channel(user_id: int) -> bool:
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChatMember"
    params = {"chat_id": settings.CHANNEL_ID, "user_id": user_id}

    async with ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()

    if not data.get("ok"):
        print("Ошибка при проверке доступа:", data)
        return False

    status = data["result"]["status"]
    return status in ("member", "administrator", "creator")


@onboarding_router.message(Command("start"))
async def command_start_handler(message: Message, session: AsyncSession) -> None:
    
    user_id = message.from_user.id
    is_member = await is_user_in_channel(user_id)
    if not is_member:
        await message.answer(
            "⚠️ Доступ запрещён.\n"
            f"Пожалуйста, подпишись на канал , чтобы использовать бота."
        )
        return
    user: User = await read_user(session=session, user_id=user_id)
    if user is None:
        user = User(
            id=user_id,
            is_bot=message.from_user.is_bot,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
            is_premium=message.from_user.is_premium,
        )
        await create_user(session=session, user=user)
        print(f"user created {user.username}")
    chat_id = message.chat.id
    chat: Chat = await read_chat(session=session, chat_id=chat_id)
    if chat is None:
        chat = Chat(
            id=chat_id,
            type=message.chat.type,
            title=message.chat.title,
            user_id=message.from_user.id,
        )
        await create_chat(session=session, chat=chat)
        print(f"chat created for user {user_id} chat {chat.id}")
    # await message.answer(f"{user.username} and chat_id {chat.id}")
    await message.answer(
        "Привет! Я бот для проведения тестов по знанию компании TrustMe.\nЧтобы начать тест, используй команду /test. Удачи!,\n/qa - вопросы и ответы,\n/me - информация о вас",
    )


@onboarding_router.message(Command("me"))
async def me(message: Message):
    user = message.from_user
    chat = message.chat

    info = (
        f"🧍‍♂️ <b>Информация о пользователе</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🤖 Бот: {'Да' if user.is_bot else 'Нет'}\n"
        f"👤 Имя: {user.first_name}\n"
        f"👥 Фамилия: {user.last_name or '—'}\n"
        f"💬 Username: @{user.username if user.username else '—'}\n"
        f"🌐 Язык: {user.language_code or '—'}\n"
        f"💎 Premium: {'Да' if user.is_premium else 'Нет'}\n\n"
        f"💭 <b>Информация о чате</b>\n"
        f"🏷️ Chat ID: <code>{chat.id}</code>\n"
        f"📨 Message ID: <code>{message.message_id}</code>\n"
        f"💬 Chat type: {chat.type}\n"
        f"📛 Chat title: {chat.title or '—'}"
    )

    await message.answer(info, parse_mode="HTML")
