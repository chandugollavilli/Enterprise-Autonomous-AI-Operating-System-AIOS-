import pytest
from src.cli.platform_cli import PlatformCLI


def test_platform_cli_commands():
    cli = PlatformCLI()

    res_login = cli.run_command(["login"])
    assert "Successfully logged in" in res_login

    res_upload = cli.run_command(["upload", "contract.pdf"])
    assert "Document uploaded successfully" in res_upload

    res_search = cli.run_command(["search", "indemnification"])
    assert "Search Results" in res_search
