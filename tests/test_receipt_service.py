import json
import os
from pathlib import Path
import subprocess
import sys

from src.receipt_service import ReceiptRequest, send_receipt


def test_documented_entry_point_imports_service():
    root = Path(__file__).resolve().parent.parent
    environment = os.environ.copy()
    environment.pop("RECEIPT_TO", None)
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "send_receipt.py")],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "set RECEIPT_TO" in result.stderr


class FakeResponse:
    status = 200

    def read(self):
        return json.dumps({"ok": True, "data": {"message_id": "m-1"}}).encode()


def test_receipt_request_builds_business_subject(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    seen = {}

    def opener(request, timeout):
        seen["method"] = request.get_method()
        seen["body"] = json.loads(request.data)
        return FakeResponse()

    result = send_receipt(
        ReceiptRequest("tenant@example.com", "Li", "Cedar Court", 9900, "r-9"),
        opener=opener,
    )
    assert result["message_id"] == "m-1"
    assert seen["method"] == "POST"
    assert seen["body"]["subject"] == "Rent receipt r-9 - Cedar Court"
    assert "9900" not in seen["body"]["html"]
