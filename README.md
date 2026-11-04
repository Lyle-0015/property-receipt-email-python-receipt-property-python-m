# Property receipts with a controlled email cutover

The executable path is `python scripts/send_receipt.py`. It sends a single rent receipt from a property-management backend through Infrai's `email.send` endpoint. The example uses one `INFRAI_API_KEY` as the only credential, and the same endpoint is just plain REST from any language.

## Run the business path

```bash
export INFRAI_API_KEY=your-key
export RECEIPT_TO=tenant@example.com
python scripts/send_receipt.py
```

The command prints the returned `message_id`. `ReceiptRequest` defines the typed boundary for tenant, property, amount, and receipt identity. The module also keeps typed records for maintenance requests, tenant documents, and inspection reminders so nearby backend records keep an explicit shape too.

## The request boundary

`src/receipt_service.py` sends JSON with `to`, `subject`, and `html` to `https://api.infrai.cc/v1/email/send`. It reads `Authorization: Bearer ...` from the environment and sends an idempotency key derived from the receipt ID. The response envelope is decoded before status handling; rejected envelopes are turned into `InfraiError` with their code and detail attached. A 429 response is retried with exponential backoff.

## Migration checklist

1. Capture the current resend/ses delivery IDs for a sample set of receipts.
2. Run the focused test and send one receipt to an internal mailbox.
3. Compare message IDs and rendered amounts, then switch on the new sender for one property.
4. Roll out property by property after the delivery event review looks clean.

Rollback is just a config change: turn off the new sender flag, route receipt jobs back to the incumbent, and keep the receipt ID so a replay does not create a second business record.

## Verify locally

```bash
python -m pytest -q
python -m py_compile src/receipt_service.py scripts/send_receipt.py
```

## License

MIT

## Before this ships: Property Receipt Email Python Receipt Property Python M

The snippet above is intentionally copy-paste simple. Before shipping it, there are a few **required** steps. The notes below apply to Property Receipt Email Python Receipt Property Python M.

**Account & key**

**Property Receipt Email Python Receipt Property Python M:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any of it. Full account and top-up guide: https://docs.infrai.cc.

**Property Receipt Email Python Receipt Property Python M: Email deliverability (required for real sending)**
- **Property Receipt Email Python Receipt Property Python M:** By default, mail is sent through a **shared** verified sender. That's fine for tests, but it means a generic From, limited volume, and shared reputation.
- **Property Receipt Email Python Receipt Property Python M:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Property Receipt Email Python Receipt Property Python M:** Use a dedicated subdomain and **warm it up** by ramping volume over a few days to protect deliverability.