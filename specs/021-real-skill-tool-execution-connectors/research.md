# Research: Real Skill Tool Execution Connectors

## Decision: Use `SkillExecutionGateway` As The Runtime Boundary

**Rationale**: The feature needs a single policy and observability choke point before any adapter can run. `SkillExecutionGateway` is explicit enough for runtime graph role nodes and admin diagnostics, while avoiding direct adapter imports from graph execution code.

**Alternatives Considered**:

- Direct adapter calls from graph nodes: rejected because policy, credential, redaction, and audit checks could be bypassed.
- Embedding adapters inside skill registry services: rejected because registry lifecycle and runtime execution have different responsibilities.

## Decision: Evaluate Policy Before Credential Materialization Or Adapter Invocation

**Rationale**: Installation/version, tool policy, outbound allowlist, side-effect policy, tenant isolation, and execution mode are cheap checks that can deny unsafe requests before any external capability is touched.

**Policy Order**:

1. Tenant context and request shape.
2. Installed skill package/version and requested tool identity.
3. Tool policy allow/deny.
4. Side-effect policy.
5. Outbound domain policy.
6. Execution mode policy.
7. Credential metadata presence and tenant ownership.
8. Adapter invocation.
9. Contract validation and redacted summary persistence.

## Decision: Use Mock Fixtures As The Default Local Execution Mode

**Rationale**: Local QA must prove contracts, policies, redaction, and admin diagnostics without real Google, news, weather, or traffic credentials. Mock fixtures also make tests deterministic and fast.

**Live Probe Guardrails**:

- Disabled in local environment.
- Requires explicit `live_probe` mode.
- Requires tenant installation and credential metadata.
- Requires outbound allowlist for adapter domains.
- Persists only safe summaries and artifact references.

## Decision: Treat All 021 Adapters As Read-Only

**Rationale**: Daily Briefing only needs reads. Write operations, calendar changes, email sends, or notification delivery are out of scope and must remain blocked by default.

## Decision: Normalize Provider-Specific Output Into Workflow Contracts

**Rationale**: Workflow graph nodes should consume stable contracts rather than provider payloads. Adapter-specific parsing is hidden behind the gateway.

**Contract Families**:

- Calendar events: title, starts_at, ends_at, location, priority, conflict flag.
- Gmail messages: sender, subject, received_at, action_required, urgency, summary.
- News items: headline, source, url, published_at, relevance, summary.
- Weather forecast: location, forecast_date, condition, high/low, precipitation chance.
- Commute lookup: origin label, destination label, mode, estimated minutes, status.

## Decision: Redact And Summarize Rather Than Persist Raw Payloads

**Rationale**: Raw provider payloads may contain secrets, PII, email bodies, and sensitive URL query parameters. Inline persistence stores only operation identity, counts, safe fields, redacted snippets, latency, and policy decisions.

## Decision: Admin Diagnostics Are Server-Rendered

**Rationale**: Existing admin console features use FastAPI/Jinja2 templates and local-principal authentication. A server-rendered diagnostics route keeps the feature aligned with established admin UI patterns and Playwright validation.

## Open Items Resolved By Autopilot

- Live calls are staging-only probes, not local QA requirements.
- No side-effecting adapter is in scope.
- Raw external payloads are not stored inline.
