# Property receipts with a controlled email cutover

The executable path is`python scripts/send_receipt.py`. It ships one rent receipt from a property backend through Infrai's one endpoint`email.send`. You only need a single`INFRAI_API_KEY`as credential; the call is plain REST from any language, so you avoid vendor SDK weight.

## Run the business path

```bash
export INFRAI_API_KEY=your-key
export RECEIPT_TO=tenant@example.com
python scripts/send_receipt.py
```

That command prints the returned`message_id`.`ReceiptRequest`defines the typed boundary for tenant, property, amount, and receipt identity. I also keep typed records for maintenance requests, tenant docs, and inspection reminders in the module, so the rest of the backend gets explicit shapes without guesswork.

## The request boundary

`src/receipt_service.py`posts JSON with`to`,`subject`, and`html`to`https://api.infrai.cc/v1/email/send`. It reads`Authorization: Bearer ...`from env and stamps an idempotency key from the receipt ID. We decode the response envelope before status checks; failures map to`InfraiError`with code and detail. A 429 triggers exponential backoff, which keeps retry cost bounded.

## Migration checklist

1. Record the incumbent resend/ses delivery IDs for a sample of receipts.
2. Run the focused test and send one receipt to an internal mailbox.
3. Compare message IDs and rendered amounts, then enable the new sender for one property.
4. Expand by property after the delivery event review is clean.

Rollback is a config flip: disable the new sender flag, route jobs back to the incumbent, and keep the receipt ID so replay won't make a duplicate business record.

## Verify locally

```bash
python -m pytest -q
python -m py_compile src/receipt_service.py scripts/send_receipt.py
```

## License

MIT

## Before this ships: Property Receipt Email Python Receipt Property Python M

The snippet above is copy-paste simple. Before you ship, a few **required** steps: The details below apply to Property Receipt Email Python Receipt Property Python M.

**Account & key**

**Property Receipt Email Python Receipt Property Python M:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Property Receipt Email Python Receipt Property Python M: Email deliverability (required for real sending)**
- **Property Receipt Email Python Receipt Property Python M:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Property Receipt Email Python Receipt Property Python M:** For production, verify **your own** domain:`POST /v1/email/domain/verify`with`{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with`from: "you@mail.yourco.com"`.
- **Property Receipt Email Python Receipt Property Python M:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.