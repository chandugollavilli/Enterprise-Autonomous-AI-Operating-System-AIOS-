import pytest
from src.infrastructure.connectors.s3_connector import S3ConnectorAdapter
from src.infrastructure.connectors.sftp_connector import SFTPConnectorAdapter
from src.infrastructure.connectors.connector_registry import ConnectorRegistry


@pytest.mark.asyncio
async def test_s3_connector_adapter():
    s3 = S3ConnectorAdapter(bucket_name="test-bucket")
    await s3.initialize()
    await s3.connect()

    info = s3.connector_info()
    assert info["bucket"] == "test-bucket"

    docs = await s3.list_documents()
    assert len(docs) >= 1

    content = await s3.download(docs[0]["ref"])
    assert len(content) > 0


@pytest.mark.asyncio
async def test_sftp_connector_adapter():
    sftp = SFTPConnectorAdapter(host="sftp.test.com")
    await sftp.initialize()
    await sftp.connect()

    docs = await sftp.list_documents()
    assert len(docs) >= 1


def test_connector_registry():
    s3 = S3ConnectorAdapter()
    ConnectorRegistry.register_connector("s3_default", s3)
    assert ConnectorRegistry.get_connector("s3_default") is not None
    assert len(ConnectorRegistry.list_connectors()) >= 1
