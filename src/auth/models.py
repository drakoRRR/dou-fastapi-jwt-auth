import uuid

from sqlalchemy import Boolean, Column, DateTime, String, func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base


class User(Base):
    """User model representing users in the application."""
    __tablename__ = "user"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_name = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TokenBlacklist(Base):
    """Token blacklist model representing tokens in the application."""
    __tablename__ = "token_blacklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    token = Column(String, primary_key=True, index=True)
    blacklisted_on = Column(DateTime, default=func.now())

    @classmethod
    async def find_by_id(cls, db: AsyncSession, id: UUID):
        result = await db.execute(select(cls).where(cls.id == id))
        return result.scalars().first()