from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.services.auth_service import AuthService
from src.api.dependencies import get_current_user
from src.repositories.postgres.models import User
from src.api.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    UserCreate,
    UserResponse,
    APIKeyCreate,
    APIKeyResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        user = await auth_service.create_user(
            email=req.email, password=req.password, full_name=req.full_name
        )
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            role="user",
            created_at=user.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        res = await auth_service.login(req.email, req.password)
        return TokenResponse(
            access_token=res["access_token"],
            refresh_token=res["refresh_token"],
            token_type=res["token_type"],
            expires_in=res["expires_in"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        res = await auth_service.refresh_access_token(req.refresh_token)
        return RefreshTokenResponse(
            access_token=res["access_token"],
            token_type=res["token_type"],
            expires_in=res["expires_in"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        role=current_user.role.name if current_user.role else "user",
        created_at=current_user.created_at.isoformat(),
    )


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    req: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    api_key_obj, raw_key = await auth_service.create_api_key(
        user_id=current_user.id, name=req.name, rate_limit=req.rate_limit
    )
    return APIKeyResponse(
        id=str(api_key_obj.id),
        name=api_key_obj.name,
        prefix=api_key_obj.prefix,
        api_key=raw_key,  # Full key is returned once upon creation
        rate_limit=api_key_obj.rate_limit,
        created_at=api_key_obj.created_at.isoformat(),
        is_revoked=api_key_obj.is_revoked,
    )
