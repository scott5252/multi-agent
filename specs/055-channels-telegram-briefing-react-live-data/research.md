# Research: Channels, Telegram, Briefing React Live Data

## Decision 1: Source Of Truth

**Decision**: Use existing Telegram configuration services/repositories, command alias and link-token audit services, linked identity repositories, delivery/notification repositories, channel run APIs, briefing preference services, artifact references, and audit services as authoritative data sources.

**Rationale**: These services already enforce tenant scope, redaction, idempotency, and persistence semantics. React projection builders should compose service-owned summaries rather than inventing rows.

**Alternatives considered**: Keep deterministic QA036 builders and hide them behind a service facade. Rejected because it preserves fake production data.

## Decision 2: Token And Telegram Identifier Visibility

**Decision**: Bot tokens, webhook secrets, link tokens after creation, full Telegram identifiers, authorization headers, private messages, and raw webhook payloads never render. Link token creation may return a one-time token only in the mutation response.

**Rationale**: Token and Telegram identifiers are sensitive and can appear in logs, screenshots, docs, and exports if not centrally redacted.

**Alternatives considered**: Mask tokens client-side. Rejected because sensitive values would still cross the frontend contract.

## Decision 3: Durable Actions

**Decision**: Alias save/enable/disable/delete, link-token creation/revocation, webhook validation, briefing preference save/import/export, and diagnostic refresh actions must route through existing backend services and return persisted result evidence.

**Rationale**: The live-data migration must prove action panels are not browser-only success messages.

**Alternatives considered**: Validate only read-only rendering. Rejected because the autopilot requires a user-visible persisted action for safe mutation surfaces.

## Decision 4: QA Data

**Decision**: qa055 seed scripts create real local-principal rows for Telegram config, aliases, linked identities, link-token audit, webhook receipts, deliveries, notifications, channel run references, briefing preferences, imports/exports, and audit summaries without external Telegram or provider calls.

**Rationale**: QA must prove live database behavior while staying deterministic and safe.

**Alternatives considered**: Use real Telegram webhook or Bot API probes. Rejected because local QA must not call external services.

## Decision 5: Validation

**Decision**: Completion requires QA docs, `run_spec_qa.py`, Playwright with a persisted UI action, post-UI API/database verification, and multi-agent curl regression.

**Rationale**: This matches the remove-mock-data roadmap and prevents advancement on browser-only evidence.

**Alternatives considered**: Focused unit tests only. Rejected because route, browser, persistence, and regression evidence are mandatory for each spec.
