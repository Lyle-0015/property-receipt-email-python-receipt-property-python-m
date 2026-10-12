"""Run the receipt workflow against a live Infrai account."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.receipt_service import ReceiptRequest, send_receipt


def main() -> int:
    recipient = os.environ.get("RECEIPT_TO")
    if not recipient:
        print("set RECEIPT_TO to the tenant email", file=sys.stderr)
        return 2
    result = send_receipt(
        ReceiptRequest(
            tenant_email=recipient,
            tenant_name=os.environ.get("TENANT_NAME", "Tenant"),
            property_name=os.environ.get("PROPERTY_NAME", "Harbor View"),
            amount_cents=int(os.environ.get("AMOUNT_CENTS", "125000")),
            receipt_id=os.environ.get("RECEIPT_ID", "demo-2026-09"),
        )
    )
    print(f"receipt sent; message_id={result.get('message_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
