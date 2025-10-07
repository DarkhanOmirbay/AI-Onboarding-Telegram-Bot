from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Chat


async def read_chat(session: AsyncSession, chat_id: int):
    query = select(Chat).where(Chat.id == chat_id)
    result = await session.execute(query)
    return result.scalar()


async def create_chat(session: AsyncSession, chat: Chat):
    session.add(chat)
    await session.commit()
