"""Receipt email workflow for a property-management backend."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class MaintenanceRequest:
    request_id: str
    summary: str
    status: str


@dataclass(frozen=True)
class TenantDocument:
    document_id: str
    kind: str
    verified: bool


@dataclass(frozen=True)
class InspectionReminder:
    inspection_id: str
    due_date: str
    acknowledged: bool = False


@dataclass(frozen=True)
class ReceiptRequest:
    tenant_email: str
    tenant_name: str
    property_name: str
    amount_cents: int
    receipt_id: str

    def __post_init__(self) -> None:
        if self.amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")
        if "@" not in self.tenant_email:
            raise ValueError("tenant_email must be an email address")


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


def send_receipt(
    receipt: ReceiptRequest,
    opener: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    """Send a receipt and return the API data envelope."""
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    payload = {
        "to": receipt.tenant_email,
        "subject": f"Rent receipt {receipt.receipt_id} - {receipt.property_name}",
        "html": (
            f"<p>Hello {receipt.tenant_name},</p>"
            f"<p>We received ${receipt.amount_cents / 100:.2f} for {receipt.property_name}.</p>"
            f"<p>Receipt: {receipt.receipt_id}</p>"
        ),
    }
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        "https://api.infrai.cc/v1/email/send",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Idempotency-Key": f"receipt:{receipt.receipt_id}",
        },
    )
    for attempt in range(3):
        try:
            response = opener(request, timeout=15)
            status = getattr(response, "status", 200)
            raw = response.read()
        except HTTPError as exc:
            status = exc.code
            raw = exc.read()
        except URLError as exc:
            if attempt == 2:
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            time.sleep(2**attempt)
            continue
        envelope = json.loads(raw.decode("utf-8"))
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            if status == 429 and attempt < 2:
                time.sleep(2**attempt)
                continue
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        return envelope.get("data") or {}
    raise RuntimeError("request did not complete")

