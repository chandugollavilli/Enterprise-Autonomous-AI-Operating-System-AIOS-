import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    Integer,
    BigInteger,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.models.base import BaseEntity, Base, TimestampMixin, utc_now


class RolePermission(Base):
    """Junction table for Many-to-Many relationship between Roles and Permissions."""
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )


class Permission(BaseEntity):
    """System granular permissions (e.g., document:read, ocr:execute)."""
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )


class Role(BaseEntity):
    """User Roles (e.g., Admin, Operator, Viewer)."""
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary="role_permissions", back_populates="roles", lazy="joined"
    )


class User(BaseEntity):
    """System users table."""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="users", lazy="joined")
    api_keys: Mapped[List["APIKey"]] = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")


class APIKey(BaseEntity):
    """External API authentication keys."""
    __tablename__ = "api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    rate_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # requests per minute
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="api_keys")


class Document(BaseEntity):
    """Ingested documents metadata table."""
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="documents")
    pages: Mapped[List["DocumentPage"]] = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    ocr_jobs: Mapped[List["OCRJob"]] = relationship("OCRJob", back_populates="document", cascade="all, delete-orphan")
    history: Mapped[List["ProcessingHistory"]] = relationship("ProcessingHistory", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(BaseEntity):
    """Page-level split image rendering and metrics."""
    __tablename__ = "document_pages"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    image_storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    dpi: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    deskew_angle: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="pages")
    ocr_result: Mapped[Optional["OCRResult"]] = relationship("OCRResult", back_populates="page", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("document_id", "page_number", name="uq_document_page_number"),
        Index("idx_doc_page_number", "document_id", "page_number"),
    )


class OCRJob(BaseEntity):
    """Asynchronous Celery OCR job tracking table."""
    __tablename__ = "ocr_jobs"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="ocr_jobs")


JSONType = JSON().with_variant(JSONB(), "postgresql")


class OCRResult(BaseEntity):
    """Structured OCR extraction output per page."""
    __tablename__ = "ocr_results"

    page_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_pages.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    ocr_mode: Mapped[str] = mapped_column(String(50), nullable=False)  # "base" or "gundam"
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_boxes_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    layout_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    tables_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    page: Mapped["DocumentPage"] = relationship("DocumentPage", back_populates="ocr_result")


class AuditLog(Base):
    """Enterprise compliance security audit trail."""
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    details: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")


class ProcessingHistory(Base):
    """State transition tracking history for documents."""
    __tablename__ = "processing_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_status: Mapped[str] = mapped_column(String(50), nullable=False)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    document: Mapped["Document"] = relationship("Document", back_populates="history")


class DocumentBlock(BaseEntity):
    """Structured CDM Block for document layout node storage."""
    __tablename__ = "document_blocks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    reading_order: Mapped[int] = mapped_column(Integer, nullable=False)
    bbox_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    document: Mapped["Document"] = relationship("Document")


class DocumentChunk(BaseEntity):
    """Heading-Aware Document Chunk for Phase 8 Vector Ingestion and RAG."""
    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    heading_context: Mapped[str] = mapped_column(String(512), nullable=False)
    page_references_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)

    document: Mapped["Document"] = relationship("Document")


class VectorIndex(BaseEntity):
    """Vector Index tracking entity per document chunk."""
    __tablename__ = "vector_indices"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    point_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    collection_name: Mapped[str] = mapped_column(String(100), nullable=False, default="document_chunks")
    vector_dim: Mapped[int] = mapped_column(Integer, nullable=False, default=1024)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="indexed")


class SearchHistory(BaseEntity):
    """Telemetry log for user search queries, filters, and latency."""
    __tablename__ = "search_history"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    search_type: Mapped[str] = mapped_column(String(50), nullable=False, default="hybrid")
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    filters_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class Conversation(BaseEntity):
    """Chat session entity tracking conversation memory."""
    __tablename__ = "conversations"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Conversation")
    active_llm_provider: Mapped[str] = mapped_column(String(100), nullable=False, default="openai")


class ConversationMessage(BaseEntity):
    """Message history line within a conversation session."""
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user", "assistant", "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Citation(BaseEntity):
    """Citation metadata record linked to a generated assistant message."""
    __tablename__ = "citations"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversation_messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    citation_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    heading_context: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    bbox_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    source_text: Mapped[str] = mapped_column(Text, nullable=False, default="")


class TokenUsage(BaseEntity):
    """Token consumption and estimated cost tracking."""
    __tablename__ = "token_usages"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class Tenant(BaseEntity):
    """Multi-tenant isolation entity."""
    __tablename__ = "tenants"

    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)


class Organization(BaseEntity):
    """Organization entity scoped under a tenant."""
    __tablename__ = "organizations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)


class TenantQuota(BaseEntity):
    """Tenant request, document, and storage quota limits."""
    __tablename__ = "tenant_quotas"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    max_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    max_pages_per_month: Mapped[int] = mapped_column(Integer, nullable=False, default=50000)
    max_storage_mb: Mapped[float] = mapped_column(Float, nullable=False, default=102400.0)
    current_documents_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_pages_this_month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Connector(BaseEntity):
    """Enterprise system integration connector configuration entity."""
    __tablename__ = "connectors"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    connector_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "s3", "sftp", "sharepoint"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class ConnectorSyncJob(BaseEntity):
    """Synchronization job execution tracking."""
    __tablename__ = "connector_sync_jobs"

    connector_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("connectors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    documents_synced: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class WorkflowTemplate(BaseEntity):
    """Reusable automated workflow definition template."""
    __tablename__ = "workflow_templates"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    definition_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class AutomationRule(BaseEntity):
    """Conditional document routing and action rule entity."""
    __tablename__ = "automation_rules"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_category: Mapped[str] = mapped_column(String(50), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold_value: Mapped[str] = mapped_column(String(255), nullable=False)
    target_action: Mapped[str] = mapped_column(String(100), nullable=False)


class WorkflowDefinition(BaseEntity):
    """No-code Visual Workflow Definition entity."""
    __tablename__ = "workflow_definitions"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="document_automation")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")  # "draft", "published"


class WorkflowVersion(BaseEntity):
    """Immutable version snapshot of a Visual Workflow directed graph."""
    __tablename__ = "workflow_versions"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    graph_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class WorkflowExecutionNode(BaseEntity):
    """Telemetry log for individual node execution within a workflow run."""
    __tablename__ = "workflow_execution_nodes"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ocr_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    output_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class ApprovalTask(BaseEntity):
    """Human review and approval task record."""
    __tablename__ = "approval_tasks"

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ocr_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assignee_role: Mapped[str] = mapped_column(String(50), nullable=False, default="Reviewer")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # "pending", "approved", "rejected"
    resolver_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")


class SolutionPack(BaseEntity):
    """Industry Solution Pack installation entity."""
    __tablename__ = "solution_packs"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    pack_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="installed")


class GeneratedReport(BaseEntity):
    """Persisted Executive Summary Report entity."""
    __tablename__ = "generated_reports"

    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True
    )
    pack_id: Mapped[str] = mapped_column(String(100), nullable=False)
    report_format: Mapped[str] = mapped_column(String(20), nullable=False, default="markdown")
    report_content: Mapped[str] = mapped_column(Text, nullable=False)


class DashboardConfiguration(BaseEntity):
    """Tenant Solution Pack Dashboard Metrics Configuration."""
    __tablename__ = "dashboard_configurations"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    pack_id: Mapped[str] = mapped_column(String(100), nullable=False)
    metrics_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class Extension(BaseEntity):
    """Platform registered third-party extension entity."""
    __tablename__ = "extensions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0")
    publisher: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class MarketplacePackage(BaseEntity):
    """Marketplace extension package entry."""
    __tablename__ = "marketplace_packages"

    package_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    publisher: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    downloads: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class PluginInstallation(BaseEntity):
    """Tenant installed plugin package tracking."""
    __tablename__ = "plugin_installations"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    package_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1.0.0")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class WebhookSubscription(BaseEntity):
    """HTTP Webhook Event Subscription Record."""
    __tablename__ = "webhook_subscriptions"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    target_url: Mapped[str] = mapped_column(String(512), nullable=False)
    event_types_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    secret: Mapped[str] = mapped_column(String(255), nullable=False, default="whsec_default")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class Agent(BaseEntity):
    """Specialized AIOS Autonomous Agent entity."""
    __tablename__ = "aios_agents"

    agent_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    capabilities_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class AgentSession(BaseEntity):
    """Autonomous Multi-Agent Session."""
    __tablename__ = "aios_agent_sessions"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class AgentTask(BaseEntity):
    """Sub-task execution record within multi-agent collaboration."""
    __tablename__ = "aios_agent_tasks"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aios_agent_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(String(100), nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    result_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")


class KnowledgeGraphNode(BaseEntity):
    """Enterprise Knowledge Graph Entity Node."""
    __tablename__ = "knowledge_graph_nodes"

    node_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    properties_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class KnowledgeGraphEdge(BaseEntity):
    """Enterprise Knowledge Graph Directed Edge."""
    __tablename__ = "knowledge_graph_edges"

    source_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_node_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
    properties_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class MemoryRecord(BaseEntity):
    """Hierarchical Long-Term Semantic Memory Record."""
    __tablename__ = "aios_memory_records"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    memory_type: Mapped[str] = mapped_column(String(50), nullable=False, default="conversation")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)


class PlanningGoal(BaseEntity):
    """Autonomous Planning Goal Decomposition Entity."""
    __tablename__ = "aios_planning_goals"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    tasks_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class Region(BaseEntity):
    """Global Cloud Multi-Region Record."""
    __tablename__ = "platform_regions"

    region_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cloud_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy")


class Cluster(BaseEntity):
    """Kubernetes / Cloud Infrastructure Cluster Entity."""
    __tablename__ = "platform_clusters"

    cluster_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    region_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cloud_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy")


class DigitalTwinNode(BaseEntity):
    """Digital Twin Infrastructure Topology Node."""
    __tablename__ = "digital_twin_nodes"

    node_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="healthy")


class CostRecord(BaseEntity):
    """FinOps Cloud Cost & Token Analytics Entity."""
    __tablename__ = "platform_cost_records"

    category: Mapped[str] = mapped_column(String(100), nullable=False)
    spend_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class Incident(BaseEntity):
    """SRE Incident Management Record."""
    __tablename__ = "sre_incidents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="resolved")
    auto_remediated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RunbookExecution(BaseEntity):
    """SRE Runbook Execution Audit Log."""
    __tablename__ = "sre_runbook_executions"

    runbook_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="success")
    output: Mapped[str] = mapped_column(Text, nullable=False)


class Department(BaseEntity):
    """Enterprise Department Record."""
    __tablename__ = "workforce_departments"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    manager_role: Mapped[str] = mapped_column(String(50), nullable=False, default="Manager")


class DigitalEmployee(BaseEntity):
    """Governed Enterprise Digital Employee Entity."""
    __tablename__ = "workforce_digital_employees"

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    employee_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    skills_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class BusinessProcess(BaseEntity):
    """Automated Business Process Definition Record."""
    __tablename__ = "workforce_business_processes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")


class WorkQueue(BaseEntity):
    """Departmental Work Queue Task Item."""
    __tablename__ = "workforce_work_queues"

    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")


class TaskAssignment(BaseEntity):
    """Task Assignment Record between Employee and Queue Item."""
    __tablename__ = "workforce_task_assignments"

    employee_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="in_progress")


class EscalationRule(BaseEntity):
    """Human-in-the-Loop Escalation Gate Record."""
    __tablename__ = "workforce_escalation_rules"

    employee_id: Mapped[str] = mapped_column(String(100), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    assignee_role: Mapped[str] = mapped_column(String(50), nullable=False, default="Manager")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending_human_review")
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")


class PerformanceMetric(BaseEntity):
    """Digital Workforce Performance Telemetry Record."""
    __tablename__ = "workforce_performance_metrics"

    employee_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tasks_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class FeedbackRecord(BaseEntity):
    """Human Feedback & Continuous Improvement Audit Log."""
    __tablename__ = "workforce_feedback_records"

    employee_id: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    comments: Mapped[str] = mapped_column(Text, nullable=False, default="")
