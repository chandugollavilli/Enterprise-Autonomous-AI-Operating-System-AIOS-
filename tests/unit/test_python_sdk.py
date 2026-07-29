import pytest
from sdk.python.enterprise_ocr_sdk.client import EnterpriseOCRClient


def test_enterprise_ocr_python_sdk():
    client = EnterpriseOCRClient()
    token = client.login()
    assert token is not None

    up_res = client.upload_document("test.pdf", b"pdf bytes")
    assert up_res["status"] == "uploaded"

    search_res = client.search("invoice total")
    assert len(search_res) >= 1

    chat_res = client.chat_rag("What are the payment terms?")
    assert "answer" in chat_res
