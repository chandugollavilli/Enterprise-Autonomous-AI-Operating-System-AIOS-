"""vector index and search history schema

Revision ID: 003_vector_schema
Revises: 002_layout_schema
Create Date: 2026-07-28 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003_vector_schema'
down_revision: Union[str, None] = '002_layout_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Vector Indices
    op.create_table(
        'vector_indices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('point_id', sa.String(255), nullable=False, unique=True),
        sa.Column('collection_name', sa.String(100), nullable=False, server_default='document_chunks'),
        sa.Column('vector_dim', sa.Integer(), nullable=False, server_default='1024'),
        sa.Column('status', sa.String(50), nullable=False, server_default='indexed'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_vector_indices_document_id'), 'vector_indices', ['document_id'], unique=False)
    op.create_index(op.f('ix_vector_indices_point_id'), 'vector_indices', ['point_id'], unique=True)

    # Search History
    op.create_table(
        'search_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('search_type', sa.String(50), nullable=False, server_default='hybrid'),
        sa.Column('result_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('filters_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_search_history_user_id'), 'search_history', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('search_history')
    op.drop_table('vector_indices')
