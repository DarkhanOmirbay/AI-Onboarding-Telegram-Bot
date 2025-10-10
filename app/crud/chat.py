from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Chat, Message, Response


async def read_chat(session: AsyncSession, chat_id: int):
    query = select(Chat).where(Chat.id == chat_id)
    result = await session.execute(query)
    return result.scalar()


async def create_chat(session: AsyncSession, chat: Chat):
    session.add(chat)
    await session.commit()


async def add_msg_and_rspnse(session: AsyncSession, msg: Message, rspnse: Response):
    async with session.begin():
        session.add_all([msg, rspnse])
