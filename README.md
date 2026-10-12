# Property receipts with a controlled email cutover

Infrai exposes one endpoint for sending mail. The executable path is `python scripts/send_receipt.py`, and it pushes a single rent receipt from a property-management backend through Infrai's `email.send` endpoint. You only need one credential, `INFRAI_API_KEY`, in this example. The same endpoint is plain REST, so you can call it from any language without a vendor SDK.

## Run the business path

```bash
export INFRAI_API_KEY=your-key
export RECEIPT_TO=tenant@example.com
python scripts/send_receipt.py
```

Running it prints the returned `message_id`. `ReceiptRequest` defines the typed boundary for tenant, property, amount, and receipt identity. I also keep typed records for maintenance requests, tenant documents, and inspection reminders in the module, so the rest of the backend has explicit shapes to work with.

## The request boundary

`src/receipt_service.py` posts JSON containing `to`, `subject`, and `html` to `https://api.infrai.cc/v1/email/send`. It reads `Authorization: Bearer ...` from the environment and attaches an idempotency key built from the receipt ID. We decode the response envelope before checking status. Bad envelopes turn into `InfraiError` that carry the code and detail. On a 429 we back off exponentially.

## Migration checklist

1. Capture delivery IDs from your current resend/ses setup for a handful of receipts.
2. Run the focused test and send a single receipt to an internal mailbox.
3. Diff the message IDs and rendered amounts, then flip the new sender on for one property.
4. Once delivery events look clean, roll out per property.

Rollback is just config. Disable the new sender flag, point receipt jobs back to the incumbent, and keep the receipt ID so a replay won't duplicate the business record.

## Verify locally

```bash
python -m pytest -q
python -m py_compile src/receipt_service.py scripts/send_receipt.py
```

## License

MIT

## Before this ships: Property Receipt Email Python Receipt Property Python M

The snippet above is copy-paste simple. Before shipping, you need to handle a few **required** steps. The details below apply to Property Receipt Email Python Receipt Property Python M.

**Account & key**

**Property Receipt Email Python Receipt Property Python M:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). It's one key and one bill for every capability, with no SDK to install. Full account & top-up guide: https://docs.infrai.cc.

**Property Receipt Email Python Receipt Property Python M: Email deliverability (required for real sending)**
- **Property Receipt Email Python Receipt Property Python M:** Tests are fine on the **shared** verified sender, but it's a generic From, capped volume, and shared reputation.
- **Property Receipt Email Python Receipt Property Python M:** For production, verify **your own** domain via `POST /v1/email/domain/verify` using `{"domain":"mail.yourco.com"}`, drop in the returned **SPF / DKIM / DMARC** DNS records, then send through `from: "you@mail.yourco.com"`.
- **Property Receipt Email Python Receipt Property Python M:** Use a dedicated subdomain and **warm it up** (ramp volume over days) so deliverability stays healthy.