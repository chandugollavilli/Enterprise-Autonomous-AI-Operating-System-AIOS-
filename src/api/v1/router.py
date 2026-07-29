from fastapi import APIRouter
from src.api.v1.auth import router as auth_router
from src.api.v1.health import router as health_router
from src.api.v1.documents import router as documents_router
from src.api.v1.jobs import router as jobs_router
from src.api.v1.ocr import router as ocr_router
from src.api.v1.layout import router as layout_router
from src.api.v1.admin import router as admin_router
from src.api.v1.search import router as search_router
from src.api.v1.rag import router as rag_router
from src.api.v1.tenants import router as tenants_router
from src.api.v1.automation import router as automation_router
from src.api.v1.workflow_studio import router as workflow_studio_router
from src.api.v1.solutions import router as solutions_router
from src.api.v1.marketplace import router as marketplace_router
from src.api.v1.aios import router as aios_router
from src.api.v1.global_platform import router as global_platform_router
from src.api.v1.workforce import router as workforce_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(ocr_router)
api_v1_router.include_router(layout_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(search_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(tenants_router)
api_v1_router.include_router(automation_router)
api_v1_router.include_router(workflow_studio_router)
api_v1_router.include_router(solutions_router)
api_v1_router.include_router(marketplace_router)
api_v1_router.include_router(aios_router)
api_v1_router.include_router(global_platform_router)
api_v1_router.include_router(workforce_router)
