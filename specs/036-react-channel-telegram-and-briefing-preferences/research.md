# Research: React Channel, Telegram, And Briefing Preferences

## Decision: Use Backend-Owned Safe Projections

**Rationale**: Specs 017, 022, and 023 already define tenant Telegram config, alias, delivery, linked identity, and briefing preference privacy rules. React must render explicit safe summaries from backend schemas instead of duplicating business rules.

**Alternatives considered**: Direct frontend composition from existing raw APIs was rejected because it risks exposing full Telegram identifiers, one-time tokens, private preference values, and cross-tenant diagnostics.

## Decision: Keep Local QA Mock-Safe

**Rationale**: Local and CI validation must avoid live Telegram, Auth0, credential, model provider, or connector calls. QA036 will use fake secret references, deterministic readiness, mocked webhook validation results, and safe delivery summaries.

**Alternatives considered**: Live Bot API probes were rejected because the roadmap and constitution require mock-safe default validation unless a spec explicitly approves a live probe path.

## Decision: Link Tokens Are One-Time Display Results

**Rationale**: Link tokens are sensitive. The React contract will show the token only in the immediate creation response, then show masked status, expiration, consumption state, and audit evidence on all subsequent dashboard and detail views.

**Alternatives considered**: Persistently rendering or re-copying link tokens was rejected because it creates screenshot and support-ticket leakage risk.

## Decision: Alias Management Is Tenant-Scoped And Idempotent

**Rationale**: Existing alias persistence and webhook idempotency behavior require tenant-owned create/edit/disable/delete workflows with protected alias readiness, revision/conflict handling, idempotency keys, and audit evidence.

**Alternatives considered**: Platform-global alias editing was rejected for this React slice because tenant administrators should manage only their tenant aliases.

## Decision: Delivery Diagnostics Are Bounded Safe Rows

**Rationale**: Delivery attempts and webhook receipts can contain private messages or external payloads. The React workspace will show bounded safe attempt rows with status, retry category, run link eligibility, trace/audit references, and no raw payloads.

**Alternatives considered**: Raw webhook receipt inspection was rejected because it conflicts with private message and Telegram identifier redaction.

## Decision: Run Status Links Are Safe Summaries

**Rationale**: Users benefit from status links, but run inspection can expose raw prompts, inputs, completions, and artifacts. This feature will show safe run status and next-step summaries only.

**Alternatives considered**: Embedding existing run inspection pages was rejected because it would pull broader permissions and raw-result risks into this migration slice.

## Decision: Scheduled Briefing Time Is Profile Metadata

**Rationale**: Spec 023 stores preference context, while scheduling delivery is not part of this slice. The UI will label scheduled briefing time as preference evidence until a scheduler feature exists.

**Alternatives considered**: Creating schedule jobs from this UI was rejected as scope growth and would require new durable scheduling semantics.

## Decision: Preference Import/Export Uses Safe Artifact Metadata

**Rationale**: Preference profiles include private location, VIP sender hints, topics, and account references. Import/export evidence must show safe artifact metadata, counts, revision ids, and audit references without rendering raw values.

**Alternatives considered**: Browser-side JSON preview was rejected because it would expose private preference content in screenshots.
