from enum import Enum
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger("document_intelligence.document_classifier")


class DocumentCategory(str, Enum):
    INVOICE = "Invoice"
    CONTRACT = "Contract"
    FINANCIAL_REPORT = "Financial Report"
    RESUME = "Resume"
    POLICY_DOCUMENT = "Policy Document"
    GENERAL = "General"


class DocumentClassifier:
    """Automatic Heuristic & NLP Document Classifier Engine."""

    @staticmethod
    def classify_document(text: str, filename: str = "") -> Tuple[DocumentCategory, float]:
        text_lower = text.lower()
        fn_lower = filename.lower()

        if "invoice" in text_lower or "total due" in text_lower or "tax invoice" in text_lower or "invoice" in fn_lower:
            return DocumentCategory.INVOICE, 0.95
        elif "agreement" in text_lower or "contract" in text_lower or "terms and conditions" in text_lower or "contract" in fn_lower:
            return DocumentCategory.CONTRACT, 0.92
        elif "quarterly report" in text_lower or "financial statement" in text_lower or "balance sheet" in text_lower:
            return DocumentCategory.FINANCIAL_REPORT, 0.90
        elif ("education" in text_lower or "experience" in text_lower) and ("resume" in text_lower or "cv" in text_lower or "resume" in fn_lower or "cv" in fn_lower):
            return DocumentCategory.RESUME, 0.88
        elif "policy" in text_lower or "compliance guidelines" in text_lower:
            return DocumentCategory.POLICY_DOCUMENT, 0.85

        return DocumentCategory.GENERAL, 0.70
