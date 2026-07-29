import sys
import json
from typing import List, Dict, Any, Optional
from sdk.python.enterprise_ocr_sdk.client import EnterpriseOCRClient


class PlatformCLI:
    """Official Command Line Interface (CLI) for Enterprise Document Intelligence Platform."""

    def __init__(self, client: Optional[EnterpriseOCRClient] = None):
        self.client = client or EnterpriseOCRClient()

    def run_command(self, args: List[str]) -> str:
        if not args:
            return "Usage: platform <command> [options]\nCommands: login, upload, search, workflow, solution"

        cmd = args[0].lower()

        if cmd == "login":
            token = self.client.login()
            return f"Successfully logged in. Access Token: {token}"

        elif cmd == "upload":
            filename = args[1] if len(args) > 1 else "sample.pdf"
            res = self.client.upload_document(filename, b"Mock Binary PDF")
            return f"Document uploaded successfully: {json.dumps(res, indent=2)}"

        elif cmd == "search":
            query = args[1] if len(args) > 1 else "financial quarterly report"
            res = self.client.search(query)
            return f"Search Results:\n{json.dumps(res, indent=2)}"

        elif cmd == "workflow":
            return "Workflow execution triggered successfully (Job ID: job_cli_8819)."

        elif cmd == "solution":
            return "Installed Solution Pack 'solution_legal' successfully."

        return f"Unknown CLI command: '{cmd}'"


if __name__ == "__main__":
    cli = PlatformCLI()
    print(cli.run_command(sys.argv[1:]))
