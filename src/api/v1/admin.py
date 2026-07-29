from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.database import get_db
from src.api.dependencies import get_current_user, require_permission
from src.repositories.postgres.models import User
from src.infrastructure.models.model_registry import ModelRegistry
from src.infrastructure.plugins.plugin_registry import PluginRegistry
from src.infrastructure.workflow.workflow_engine import WorkflowEngine
from src.infrastructure.feature_flags.manager import FeatureFlagManager
from src.services.analytics_service import UsageAnalyticsService
from src.api.schemas.admin import (
    ModelInfoDTO,
    PluginInfoDTO,
    WorkflowDTO,
    WorkflowStepDTO,
    FeatureFlagDTO,
    FeatureFlagUpdateRequest,
    UsageAnalyticsResponse,
)

router = APIRouter(prefix="/admin", tags=["Enterprise Administration"])


@router.get("/models", response_model=List[ModelInfoDTO])
async def list_registered_models(current_user: User = Depends(get_current_user)):
    """List registered AI models (OCR, Embedding, LLM, Reranker)."""
    models = ModelRegistry.list_models()
    return [
        ModelInfoDTO(
            name=m.name,
            category=m.category,
            provider=m.provider,
            version=m.version,
            capabilities=m.capabilities,
            is_default=m.is_default,
            health_status=m.health_status,
        )
        for m in models
    ]


@router.get("/plugins", response_model=List[PluginInfoDTO])
async def list_registered_plugins(current_user: User = Depends(get_current_user)):
    """List registered processing and exporter plugins."""
    plugins = PluginRegistry.list_plugins()
    return [
        PluginInfoDTO(
            name=p.name,
            category=p.category,
            version=p.version,
            description=p.description,
            author=p.author,
        )
        for p in plugins
    ]


@router.get("/workflows", response_model=List[WorkflowDTO])
async def list_registered_workflows(current_user: User = Depends(get_current_user)):
    """List registered document processing pipelines."""
    workflows = list(WorkflowEngine._workflows.values())
    return [
        WorkflowDTO(
            workflow_id=w.workflow_id,
            name=w.name,
            steps=[
                WorkflowStepDTO(
                    step_id=s.step_id,
                    name=s.name,
                    action_name=s.action_name,
                    is_optional=s.is_optional,
                )
                for s in w.steps
            ],
        )
        for w in workflows
    ]


@router.get("/feature-flags", response_model=List[FeatureFlagDTO])
async def list_feature_flags(current_user: User = Depends(get_current_user)):
    """List runtime feature flags and current toggle states."""
    flags = FeatureFlagManager.list_flags()
    return [FeatureFlagDTO(name=k, enabled=v) for k, v in flags.items()]


@router.post("/feature-flags/{flag_name}", response_model=FeatureFlagDTO)
async def toggle_feature_flag(
    flag_name: str,
    payload: FeatureFlagUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update runtime feature flag state."""
    FeatureFlagManager.set_flag(flag_name, payload.enabled)
    return FeatureFlagDTO(name=flag_name, enabled=payload.enabled)


@router.get("/analytics", response_model=UsageAnalyticsResponse)
async def get_usage_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve enterprise platform throughput, document, page, and storage usage statistics."""
    analytics_service = UsageAnalyticsService(db)
    metrics = await analytics_service.get_usage_metrics()
    return UsageAnalyticsResponse(**metrics)
