import unittest
from src.config import settings


class TestConfig(unittest.TestCase):
    def test_settings_default_values(self):
        self.assertEqual(settings.PROJECT_NAME, "Enterprise Document Intelligence Platform")
        self.assertEqual(settings.API_V1_STR, "/api/v1")
        self.assertEqual(settings.POSTGRES_PORT, 5432)
        self.assertEqual(settings.MINIO_BUCKET_NAME, "documents")

    def test_database_uri_generation(self):
        async_uri = settings.SQLALCHEMY_DATABASE_URI
        self.assertTrue(async_uri.startswith("postgresql+asyncpg://"))

        sync_uri = settings.SQLALCHEMY_SYNC_DATABASE_URI
        self.assertTrue(sync_uri.startswith("postgresql://"))


if __name__ == "__main__":
    unittest.main()
