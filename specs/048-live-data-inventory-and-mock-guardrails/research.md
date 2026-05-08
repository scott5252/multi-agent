# Research: Live Data Inventory And Mock Guardrails

## Decision: Use A Deterministic Filesystem Scanner

Use a Python scanner under `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py` that reads production backend source, production frontend source, generated contracts, and built assets. The scanner returns typed findings and can be invoked by tests and the migration dashboard.

**Rationale**: The target is production code and response surfaces, not durable user state. A deterministic scanner is reviewable, works in CI, and avoids new storage or background jobs.

**Alternatives considered**: A database-backed scan history was rejected because Spec 048 only needs current repository evidence. A shell-only `rg` check was rejected because severity, allowlists, replacement specs, and redaction-safe output need structured classification.

## Decision: Separate Current Legacy Findings From New Regressions

Classify known roadmap findings as mapped legacy findings with replacement specs, while treating new unallowlisted production fixture markers as CI-blocking.

**Rationale**: Specs 050 through 057 still need to remove existing domain builders. Spec 048 must not block itself on current known findings, but it must prevent expansion while the cleanup proceeds.

**Alternatives considered**: Failing on every current finding would stop the roadmap at Spec 048. Allowing all current markers without replacement mapping would weaken the gate and invite hidden regressions.

## Decision: Allow Only Derived Computed System Metadata

Allow computed metadata when derived from code, configuration, route registration, feature flags, asset manifests, or scanner output. Require each allowlist entry to name the source and reason.

**Rationale**: Migration and route safety panels legitimately report system state. The rule preserves those panels while banning fake workflows, fake users, fake usage events, fake audit references, and similar domain rows.

**Alternatives considered**: A broad migration-dashboard exemption was rejected because it could hide fixture data. A no-exception rule was rejected because asset and route inventory are not domain data.

## Decision: Route Target Registry For Response Scans

Define an explicit route target list for production `/admin/app` JSON endpoints, including principal, tenant scope, and whether the target is empty-state, seeded-state, or computed-metadata only.

**Rationale**: The scanner needs deterministic coverage and safe principals. Route targets in code are easier to test and review than scraping every FastAPI route dynamically without context.

**Alternatives considered**: Pure FastAPI route introspection was rejected because some routes require path parameters or safe mutations. Manual docs-only coverage was rejected because it cannot fail CI.

## Decision: Expose Inventory Through Migration Dashboard

Add a live-data inventory endpoint and render summary evidence in the existing migration hardening UI.

**Rationale**: Reviewers already use `/admin/app/migration` for decommission evidence. Keeping the new evidence there avoids a new workspace and keeps Spec 048 scoped.

**Alternatives considered**: A standalone admin page was rejected as unnecessary surface area. Artifact-only output was rejected because the roadmap requires browser-first QA evidence.

## Decision: No Live Provider Or External Calls

All scanner, route response, and Playwright validation must use local-principal or Auth0-shaped test principals, QA databases, deterministic services, and existing mocked-safe paths.

**Rationale**: The constitution and roadmap prohibit accidental live provider, Telegram, credential, connector, or outbound calls during cleanup validation.

**Alternatives considered**: Real provider probes were rejected because Spec 048 is inventory/guardrail work, not provider readiness validation.
