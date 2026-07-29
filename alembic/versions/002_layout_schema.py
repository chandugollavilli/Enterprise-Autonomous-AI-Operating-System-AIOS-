"""layout and chunking schema

Revision ID: 002_layout_schema
Revises: 001_initial_schema
Create Date: 2026-07-28 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_layout_schema'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Document Blocks
    op.create_table(
        'document_blocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('reading_order', sa.Integer(), nullable=False),
        sa.Column('bbox_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_document_blocks_document_id'), 'document_blocks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_blocks_node_type'), 'document_blocks', ['node_type'], unique=False)
    op.create_index(op.f('ix_document_blocks_page_number'), 'document_blocks', ['page_number'], unique=False)

    # Document Chunks
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('heading_context', sa.String(512), nullable=False),
        sa.Column('page_references_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('qdrant_point_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_qdrant_point_id'), 'document_chunks', ['qdrant_point_id'], unique=True)


def downgrade() -> None:
    op.drop_table('document_chunks')
    op.drop_table('document_blocks')
