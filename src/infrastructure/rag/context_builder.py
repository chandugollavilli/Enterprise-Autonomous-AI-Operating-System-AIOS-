from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger("document_intelligence.context_builder")


class ContextBuilder:
    """Assembles retrieved search chunks into clean formatted prompt context strings with token budgeting."""

    @staticmethod
    def build_context(
        search_results: List[Dict[str, Any]], max_tokens: int = 4000
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Format search results into numbered context blocks:
        [1] Context Content (Heading: Section 1, Page 1)
        [2] Context Content (Heading: Section 2, Page 2)
        """
        context_blocks: List[str] = []
        referenced_items: List[Dict[str, Any]] = []

        total_words = 0

        for idx, item in enumerate(search_results, start=1):
            payload = item.get("payload", {})
            content = payload.get("content", "").strip()
            heading = payload.get("heading_context", "")
            pages = payload.get("pages", [])

            words = len(content.split())
            if total_words + words > max_tokens:
                logger.info(f"Token budget limit ({max_tokens} words) reached at context item [{idx}]")
                break

            page_str = f"Page {pages[0]}" if pages else ""
            header_line = f"[{idx}] (Header: {heading} | {page_str})" if heading else f"[{idx}] ({page_str})"
            block = f"{header_line}\n{content}"

            context_blocks.append(block)
            item["citation_index"] = idx
            referenced_items.append(item)
            total_words += words

        formatted_context_str = "\n\n".join(context_blocks)
        return formatted_context_str, referenced_items
