import uuid
import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repositories.postgres.models import Document, DocumentBlock, DocumentChunk, OCRResult
from src.repositories.postgres.document_repo import DocumentRepository
from src.domain.interfaces.storage_gateway import IStorageGateway
from src.domain.layout.canonical_model import CanonicalDocument, CanonicalNode, NodeType
from src.infrastructure.layout.reading_order import ReadingOrderEngine
from src.infrastructure.layout.block_classifier import BlockClassifier
from src.infrastructure.layout.exporters.markdown_exporter import MarkdownGenerator
from src.infrastructure.layout.exporters.html_exporter import HTML5Generator
from src.infrastructure.layout.exporters.json_exporter import JSONExporter
from src.infrastructure.layout.chunker import HeadingAwareChunker

logger = logging.getLogger("document_intelligence.layout_service")


class LayoutService:
    """Enterprise Document Layout Analysis, CDM Construction, Exporting, and Chunking Service."""

    def __init__(self, db_session: AsyncSession, storage_gateway: IStorageGateway):
        self.db = db_session
        self.doc_repo = DocumentRepository(db_session)
        self.storage = storage_gateway

    async def build_canonical_document(self, document_id: uuid.UUID) -> CanonicalDocument:
        """Construct Canonical Document Model (CDM) tree from page OCR results."""
        doc = await self.doc_repo.get_with_pages_and_ocr(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        canonical_doc = CanonicalDocument(document_id=str(doc.id))

        for page in doc.pages:
            if not page.ocr_result:
                continue

            raw_boxes = page.ocr_result.raw_boxes_json.get("boxes", [])
            page_nodes: List[CanonicalNode] = []

            for box_item in raw_boxes:
                bbox = box_item["box"]
                text = box_item["text"]
                node = BlockClassifier.classify(text=text, bbox=bbox, page_number=page.page_number)
                node.confidence = box_item.get("confidence", 1.0)
                page_nodes.append(node)

            # Sort nodes per page using spatial reading order engine
            sorted_page_nodes = ReadingOrderEngine.sort_nodes(page_nodes)
            canonical_doc.nodes.extend(sorted_page_nodes)

        return canonical_doc

    async def process_and_persist_layout(
        self, document_id: uuid.UUID
    ) -> Tuple[CanonicalDocument, str, str, List[DocumentChunk]]:
        """
        Process Layout Intelligence:
        CDM -> Markdown -> HTML5 -> JSON -> Chunks -> Database Persistence.
        """
        cdm = await self.build_canonical_document(document_id)

        # Generate Exporter Formats
        markdown_content = MarkdownGenerator.generate(cdm)
        html_content = HTML5Generator.generate(cdm)

        # Chunk Document
        chunker = HeadingAwareChunker(max_tokens=600)
        chunk_dtos = chunker.chunk_document(cdm)

        # Clear existing blocks and chunks for re-processing
        await self.db.execute(select(DocumentBlock).where(DocumentBlock.document_id == document_id))

        # Save DocumentBlocks to PostgreSQL
        for node in cdm.get_ordered_nodes():
            block_record = DocumentBlock(
                document_id=document_id,
                node_type=node.node_type.value,
                page_number=node.page_number,
                reading_order=node.reading_order,
                bbox_json={"bbox": node.bbox},
                text=node.text,
                confidence=node.confidence,
            )
            self.db.add(block_record)

        # Save DocumentChunks to PostgreSQL
        created_chunks: List[DocumentChunk] = []
        for dto in chunk_dtos:
            chunk_record = DocumentChunk(
                document_id=document_id,
                chunk_index=dto.chunk_index,
                content=dto.content,
                heading_context=dto.heading_context,
                page_references_json={"pages": dto.page_references, "bboxes": dto.bboxes},
            )
            self.db.add(chunk_record)
            created_chunks.append(chunk_record)

        # Update Document status
        doc = await self.doc_repo.get_by_id(document_id)
        if doc:
            doc.status = "structured"
            await self.doc_repo.update(doc)

        await self.db.commit()

        return cdm, markdown_content, html_content, created_chunks
