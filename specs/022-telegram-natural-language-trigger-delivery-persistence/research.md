# Research: Telegram Natural-Language Trigger Delivery Persistence

## Decision: Tenant-Scoped Exact Alias Matching

**Rationale**: The feature needs predictable, auditable routing for phrases such as `Morning briefing` and commands such as `/briefing`. Exact matching after trimming, whitespace normalization, and case folding avoids ambiguous fuzzy routing while still supporting natural language aliases.

**Alternatives considered**:

- Fuzzy semantic matching: deferred because it would require model policy, confidence thresholds, and additional tenant safety review.
- Global alias registry: rejected because tenants can use the same alias text for different workflow versions.

## Decision: Persistent Token Audits Plus Runtime Identity Links

**Rationale**: Existing Telegram admin configuration already persists link token audits and masked identity summaries. The runtime webhook needs restart-safe token consumption and identity lookup, so the implementation reuses token audits for token status and stores active Telegram identity links in the channel persistence table.

**Alternatives considered**:

- Keep in-memory link state: rejected because it fails restart durability.
- Store raw token values: rejected because it violates secret hygiene and admin redaction requirements.

## Decision: Update Receipt Table For Webhook Idempotency

**Rationale**: Telegram retries updates by `update_id`. A dedicated update receipt with safe stored response provides replay before identity resolution and prevents duplicate run creation or duplicate delivery.

**Alternatives considered**:

- Use in-memory update map only: rejected because it fails restart durability.
- Force update receipts into generic idempotency records: rejected because Telegram update replay happens before platform identity is always known.

## Decision: Bot API Boundary With Mocked Local QA

**Rationale**: Production delivery should be isolated behind a small `sendMessage` client that receives a configured secret reference, while local and CI validation must avoid real external side effects. Tests inject a mock client through container state and verify request shape plus persisted attempt evidence.

**Alternatives considered**:

- Direct `httpx.post` inside the webhook handler: rejected because it would be harder to test and easier to leak token handling.
- No delivery boundary until worker completion: rejected because the feature requires final Telegram delivery evidence.

## Decision: Reuse Notification Delivery Attempts

**Rationale**: Existing channel schema already has notification delivery attempt records with tenant, run, channel, event, status, provider ID, retry, and trace fields. Reusing this table keeps delivery evidence consistent across channel notifications.

**Alternatives considered**:

- Create a Telegram-specific delivery table: rejected as redundant for v1.
- Persist only diagnostics: rejected because diagnostics do not provide retry-safe attempt-level evidence.

## Decision: Deterministic Daily Briefing QA Completion

**Rationale**: Specs 020 and 021 close graph execution and tool execution gaps, but this feature must validate Telegram delivery without real providers. Alias-triggered QA can use existing deterministic channel completion input to produce a safe final briefing-like result and exercise delivery.

**Alternatives considered**:

- Wait for a background worker in API tests: rejected because it would make local QA slower and more brittle.
- Use live Calendar/Gmail/news/weather tools: rejected by the no external side effects policy.
