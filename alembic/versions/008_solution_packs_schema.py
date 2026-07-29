"""solution packs, generated reports, and dashboard configurations schema

Revision ID: 008_solution_packs_schema
Revises: 007_workflow_studio_schema
Create Date: 2026-07-29 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '008_solution_packs_schema'
down_revision: Union[str, None] = '007_workflow_studio_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Solution Packs
    op.create_table(
        'solution_packs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('pack_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False, server_default='v1.0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='installed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_solution_packs_tenant_id'), 'solution_packs', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_solution_packs_pack_id'), 'solution_packs', ['pack_id'], unique=False)

    # Generated Reports
    op.create_table(
        'generated_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=True),
        sa.Column('pack_id', sa.String(100), nullable=False),
        sa.Column('report_format', sa.String(20), nullable=False, server_default='markdown'),
        sa.Column('report_content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_generated_reports_document_id'), 'generated_reports', ['document_id'], unique=False)

    # Dashboard Configurations
    op.create_table(
        'dashboard_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('pack_id', sa.String(100), nullable=False),
        sa.Column('metrics_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_dashboard_configurations_tenant_id'), 'dashboard_configurations', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_table('dashboard_configurations')
    op.drop_table('generated_reports')
    op.drop_table('solution_packs')
