# Contract: Telegram Alias Delivery

## Admin Alias API

### `GET /admin/telegram/api/aliases?tenant_id=<uuid>`

Returns tenant-scoped aliases visible to the authorized principal.

```json
{
  "items": [
    {
      "telegram_command_alias_id": "00000000-0000-0000-0000-000000000000",
      "tenant_id": "11111111-1111-1111-1111-111111111111",
      "alias_text": "Morning briefing",
      "alias_normalized": "morning briefing",
      "published_workflow_version_id": "22222222-2222-2222-2222-222222222222",
      "description": "Daily Intelligence Briefing",
      "protected": true,
      "enabled": true,
      "revision_token": "opaque",
      "updated_by_principal_id": "tenant-admin-acme",
      "created_at": "2026-05-04T00:00:00Z",
      "updated_at": "2026-05-04T00:00:00Z"
    }
  ]
}
```

### `POST /admin/telegram/api/aliases`

Creates or updates one alias by tenant and normalized text.

```json
{
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "alias_text": "Morning briefing",
  "published_workflow_version_id": "22222222-2222-2222-2222-222222222222",
  "description": "Daily Intelligence Briefing",
  "protected": true,
  "enabled": true,
  "revision_token": null
}
```

Responses:

- `200 OK`: alias created or updated.
- `403 Forbidden`: principal is not authorized for tenant scope.
- `409 Conflict`: stale revision token.
- `422 Unprocessable Entity`: alias text or workflow version is invalid.

## Telegram Webhook Alias Routing

### `POST /channels/telegram/webhook/{secret}`

When message text is not a built-in command:

1. Verify webhook secret.
2. Replay `telegram_update_receipts` if `update_id` was already handled.
3. Resolve persistent Telegram identity by user/chat.
4. Check admin identity summary has not been revoked.
5. Check tenant Telegram configuration is enabled and provider-ready.
6. Normalize message text and find enabled tenant alias.
7. Start the published workflow version through `ChannelService.start_run`.
8. Format deterministic final result when available.
9. Send via Bot API client boundary.
10. Persist a delivery attempt and update receipt.

Safe response example:

```json
{
  "ok": true,
  "messages": ["Daily Intelligence Briefing delivered."],
  "run_id": "33333333-3333-3333-3333-333333333333",
  "alias": "Morning briefing",
  "delivered": true
}
```

## Bot API Client Boundary

```python
async def send_message(
    *,
    token_ref: str,
    chat_id: int,
    text: str,
    trace_id: str,
) -> TelegramBotApiSendResult: ...
```

Requirements:

- `token_ref` is a configured secret reference label, not a raw persisted token.
- Local and CI tests use a mock client.
- Message text is sanitized and bounded before sending.
- Result exposes only `ok`, optional provider message ID, HTTP status, and safe failure category.

## Delivery Attempt Evidence

Every physical send attempt creates one `notification_delivery_attempts` record.

Required safe fields:

- `tenant_id`
- `run_id`
- `channel_type=telegram`
- `event_type=terminal`
- `payload_fingerprint`
- `delivery_status`
- `provider_message_id`
- `failure_category`
- `attempt_number`
- `next_retry_at`
- `trace_id`

No raw bot token, webhook secret, link token, prompt body, or full Telegram identifier may be stored.
