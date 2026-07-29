import os
import pytest
from src.infrastructure.secrets.secrets_manager import EnvSecretsManager, VaultSecretsManager


def test_env_secrets_manager():
    os.environ["TEST_SECRET_KEY"] = "super-secret-pass"
    mgr = EnvSecretsManager()
    val = mgr.get_secret("TEST_SECRET_KEY")
    assert val == "super-secret-pass"

    val_fallback = mgr.get_secret("NON_EXISTENT_KEY", default="default-value")
    assert val_fallback == "default-value"


def test_vault_secrets_manager_fallback():
    os.environ["VAULT_TEST_KEY"] = "vault-secret-val"
    vault_mgr = VaultSecretsManager()
    val = vault_mgr.get_secret("VAULT_TEST_KEY")
    assert val == "vault-secret-val"
