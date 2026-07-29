import uuid
from typing import Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.postgres.user_repo import UserRepository, APIKeyRepository
from src.repositories.postgres.models import User, APIKey
from src.infrastructure.security.password import verify_password, hash_password
from src.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_token
from src.infrastructure.security.api_key import generate_api_key, hash_api_key


class AuthService:
    """Authentication and Authorization Business Logic Service."""

    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.api_key_repo = APIKeyRepository(session)

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password.")
        if not user.is_active:
            raise ValueError("User account is disabled.")
        return user

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        user = await self.authenticate_user(email, password)
        role_name = user.role.name if user.role else "user"
        claims = {"role": role_name}
        
        access_token = create_access_token(subject=user.id, claims=claims)
        refresh_token = create_refresh_token(subject=user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": role_name,
            },
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type. Refresh token required.")

        user_id = uuid.UUID(payload["sub"])
        user = await self.user_repo.get_with_role_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User account is inactive or not found.")

        role_name = user.role.name if user.role else "user"
        access_token = create_access_token(subject=user.id, claims={"role": role_name})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,
        }

    async def create_user(
        self, email: str, password: str, full_name: str | None = None, is_superuser: bool = False
    ) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists.")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_superuser=is_superuser,
        )
        return await self.user_repo.create(user)

    async def create_api_key(self, user_id: uuid.UUID, name: str, rate_limit: int = 100) -> Tuple[APIKey, str]:
        full_key, prefix, key_hash = generate_api_key()
        api_key = APIKey(
            user_id=user_id,
            name=name,
            prefix=prefix,
            key_hash=key_hash,
            rate_limit=rate_limit,
        )
        created = await self.api_key_repo.create(api_key)
        return created, full_key

    async def validate_api_key(self, raw_key: str) -> APIKey:
        key_hash = hash_api_key(raw_key)
        api_key = await self.api_key_repo.get_by_key_hash(key_hash)
        if not api_key:
            raise ValueError("Invalid or revoked API key.")
        return api_key
