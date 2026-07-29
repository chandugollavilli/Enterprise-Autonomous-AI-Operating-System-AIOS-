import uuid
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.repositories.postgres.user_repo import UserRepository, APIKeyRepository
from src.repositories.postgres.models import User
from src.infrastructure.security.jwt import decode_token
from src.infrastructure.security.api_key import hash_api_key
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.repositories.storage.factory import get_storage_gateway

bearer_security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_storage() -> IStorageGateway:
    """Dependency injection provider for object storage gateway."""
    return get_storage_gateway()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(bearer_security),
    raw_api_key: Optional[str] = Security(api_key_header),
) -> User:
    """FastAPI Security Dependency that validates JWT Access Token or X-API-Key."""
    user_repo = UserRepository(db)

    # 1. Bearer Token Auth
    if auth_header and auth_header.credentials:
        try:
            payload = decode_token(auth_header.credentials)
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type. Access token required.",
                )
            user_id = uuid.UUID(payload["sub"])
            user = await user_repo.get_with_role_by_id(user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive or missing.",
                )
            return user
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    # 2. X-API-Key Auth
    if raw_api_key:
        api_key_repo = APIKeyRepository(db)
        key_hash = hash_api_key(raw_api_key)
        api_key = await api_key_repo.get_by_key_hash(key_hash)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid, revoked, or expired API Key.",
            )
        user = await user_repo.get_with_role_by_id(api_key.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Associated user account is inactive.",
            )
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide a valid Bearer JWT or X-API-Key header.",
    )


def require_permission(permission_name: str):
    """RBAC Dependency Guard checking granular user permission."""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        if not current_user.role or not current_user.role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' denied.",
            )

        user_permissions = {p.name for p in current_user.role.permissions}
        if permission_name not in user_permissions and "admin:all" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required.",
            )
        return current_user

    return permission_checker
