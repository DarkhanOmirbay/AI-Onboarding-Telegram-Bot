from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Quiz


async def get_quiz(user_id: int, session: AsyncSession) -> int:
    query = select(Quiz).where(Quiz.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def create_quiz(quiz: Quiz, session: AsyncSession) -> None:
    session.add(quiz)
    await session.commit()


async def update_day(quiz: Quiz, session: AsyncSession) -> None:
    quiz.day += 1
    await session.commit()
