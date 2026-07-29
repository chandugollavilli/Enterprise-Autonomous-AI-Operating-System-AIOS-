import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repositories.postgres.base_repo import BaseRepository
from src.repositories.postgres.models import User, APIKey, Role, Permission


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = (
            select(User)
            .where(User.email == email, User.is_deleted == False)
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_role_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        query = (
            select(User)
            .where(User.id == user_id, User.is_deleted == False)
            .options(selectinload(User.role).selectinload(Role.permissions))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class APIKeyRepository(BaseRepository[APIKey]):
    def __init__(self, session: AsyncSession):
        super().__init__(APIKey, session)

    async def get_by_key_hash(self, key_hash: str) -> Optional[APIKey]:
        query = (
            select(APIKey)
            .where(APIKey.key_hash == key_hash, APIKey.is_revoked == False, APIKey.is_deleted == False)
            .options(selectinload(APIKey.user))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
