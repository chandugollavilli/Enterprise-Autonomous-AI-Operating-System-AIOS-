import pytest
from src.infrastructure.automation.document_classifier import DocumentClassifier, DocumentCategory


def test_document_classifier():
    cat1, conf1 = DocumentClassifier.classify_document("Tax Invoice - Total Due: $5,000", "invoice_123.pdf")
    assert cat1 == DocumentCategory.INVOICE
    assert conf1 > 0.90

    cat2, conf2 = DocumentClassifier.classify_document("Master Services Agreement - Terms and Conditions", "contract.pdf")
    assert cat2 == DocumentCategory.CONTRACT

    cat3, conf3 = DocumentClassifier.classify_document("Education, Work Experience, Professional Skills", "resume.pdf")
    assert cat3 == DocumentCategory.RESUME
