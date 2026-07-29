from fastapi import APIRouter, Depends, HTTPException, status
from src.config import settings
from src.infrastructure.postgres.database import check_database_health
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.api.dependencies import get_storage

router = APIRouter(tags=["Health Monitoring"])


@router.get("/health")
async def health():
    """General overall health endpoint."""
    db_ok = await check_database_health()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "disconnected",
    }


@router.get("/live")
async def liveness():
    """Kubernetes liveness probe. Fast check to verify application process is responsive."""
    return {"status": "alive"}


@router.get("/ready")
async def readiness(storage: IStorageGateway = Depends(get_storage)):
    """Kubernetes readiness probe. Checks core sub-component connectivity (DB & Storage)."""
    db_ok = await check_database_health()
    
    # Check Storage Health
    try:
        storage_ok = await storage.file_exists("health_probe_check.tmp") or True
    except Exception:
        storage_ok = False

    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "database": "down", "storage": "up" if storage_ok else "down"},
        )

    return {
        "status": "ready",
        "database": "up",
        "storage": "up" if storage_ok else "degraded",
    }
