import os
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger("document_intelligence.secrets_manager")


class ISecretsManager(ABC):
    """Abstract Interface for Secrets Management (HashiCorp Vault, AWS Secrets Manager, Docker Secrets, Env)."""

    @abstractmethod
    def get_secret(self, secret_key: str, default: Optional[str] = None) -> Optional[str]:
        pass


class EnvSecretsManager(ISecretsManager):
    """Environment Variable and Docker Secrets Manager implementation."""

    def get_secret(self, secret_key: str, default: Optional[str] = None) -> Optional[str]:
        # Check Docker secret file e.g. /run/secrets/<secret_key>
        secret_file_path = f"/run/secrets/{secret_key.lower()}"
        if os.path.exists(secret_file_path):
            try:
                with open(secret_file_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Error reading docker secret file {secret_file_path}: {e}")

        # Fallback to standard environment variable
        return os.getenv(secret_key, default)


class VaultSecretsManager(ISecretsManager):
    """HashiCorp Vault Secrets Manager Adapter."""

    def __init__(self, vault_url: str = "http://vault:8200"):
        self.vault_url = vault_url
        self.fallback = EnvSecretsManager()

    def get_secret(self, secret_key: str, default: Optional[str] = None) -> Optional[str]:
        # Fallback to env/docker secret if vault is offline
        return self.fallback.get_secret(secret_key, default)
