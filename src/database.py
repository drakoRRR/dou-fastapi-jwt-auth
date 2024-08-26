from src.config import DATABASE_URL
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

async_engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async session"""
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()