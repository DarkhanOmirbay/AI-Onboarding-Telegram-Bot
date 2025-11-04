from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User


async def read_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def create_user(session: AsyncSession, user: User):
    session.add(user)
    await session.commit()


async def update_user_department(session: AsyncSession, user_id: int, department: str):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        user.department = department
        await session.commit()
        await session.refresh(user)
        return user
    return None
