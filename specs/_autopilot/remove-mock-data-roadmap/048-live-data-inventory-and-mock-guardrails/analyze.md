# Spec 048 - Live Data Inventory And Mock Guardrails: Analyze

Roadmap source: `remove_mock_data_specs.md`

## Deterministic Targets

- Feature directory: `specs/048-live-data-inventory-and-mock-guardrails`
- Git branch: `codex/048-live-data-inventory-and-mock-guardrails`
- QA id: `qa048`
- QA database: `multi_agent_platform_qa048`
- Post-spec curl-test database: `multi_agent_curl_test`

## Global Prompt Prefix

Use the current multi-agent platform repository context after Specs 026 through
047. The React admin UI is now React-only from a presentation standpoint, but
many React JSON endpoints still return deterministic backend fixture/demo data.
The goal is to make every production React route display live, authorized data
from durable services and PostgreSQL, or an honest empty/denied/unavailable
state when no live data exists.

Preserve the constitution, specs 001 through 047, FastAPI domain services,
PostgreSQL source of truth, Auth0 production authentication,
AUTH_MODE=local_principal browser QA, tenant isolation, audit fail-closed
behavior, redaction rules, runtime version pinning, secret hygiene, object
storage boundaries, generated TypeScript contracts, Playwright evidence, QA
docs, and at least 90 percent relevant coverage.

React must consume backend-owned JSON contracts generated from Pydantic schemas.
Do not move authorization, tenant scoping, validation, credential readiness,
publish readiness, redaction, audit, or mutation decisions into browser-only
logic. Do not replace backend fixture data with frontend fixture data.

Production route handlers and projection services must not return hardcoded
domain entities, fixed qa0xx IDs, fake audit references, fake artifact
references, fake link tokens, fake run IDs, fake usage events, fake workflows,
fake providers, fake prompts, fake skill packages, fake users, or fake delivery
attempts. Test fixtures may remain in test-only directories and QA setup may
seed real databases, but production UI code must not depend on test fixture
modules.

Every spec must prove both Auth0-shaped principal behavior with backend route
tests and local-principal behavior with browser Playwright flows. Every route
must be tested with live seeded data and with an empty database state. Empty
states must be truthful and must not invent rows.

Raw secrets, credential values, provider authorization headers, raw prompts,
raw completions, memory contents, raw run payloads, private channel messages,
raw tool payloads, raw test transcripts, full Telegram identifiers, link
tokens after creation, local filesystem paths, stack traces, and unauthorized
tenant labels must never appear in React UI, redirects, exports, screenshots,
QA artifacts, logs, or docs.

## Analyze Prompt

Analyze the live data inventory for missed production routes, overbroad
allowlists, false positives in test directories, false negatives in generated
assets, missing endpoint response scans, missing tenant/cross-tenant cases,
missing empty-state cases, and replacement specs that are too large or lack
clear durable data sources.

## Autonomous Analysis Handling

After the read-only analysis report, remediate CRITICAL/HIGH findings only when the fix is explicit from the roadmap or local artifacts, then rerun analysis up to two loops. Do not implement with remaining CRITICAL findings.

## Required Post-Spec Validation Contract

After implementation, the active spec must pass QA document validation, `run_spec_qa.py`, Playwright UI validation, post-UI backend API or QA database verification, and the `multi-agent-curl-test` runner before the next spec starts. Playwright must exercise the UI; for safe mutation surfaces it must perform a user-visible action that writes through the backend and then verify persisted state through an API or redaction-safe QA database query. If any validation fails, fix only the active spec and rerun the failed command plus downstream checks.
## Roadmap Rollout Notes

- Do Spec 048 first. It should produce the authoritative worklist and prevent
  accidental expansion of mock data while later specs are in flight.
- Specs 050 through 057 can be split across independent workstreams after Spec
  049 lands, but each should own a disjoint production builder/module surface.
- Do not delete test fixture files simply because they contain `qa0xx` markers.
  The target is production UI routes and production projection services.
- Expect QA databases to need richer setup scripts. The UI should become more
  honest, not less testable.
- Each domain spec must validate both an empty live database and a seeded live
  database. This is the key behavior change from the old deterministic demo
  builders.
- Do Spec 059 after the route inventory and decommission work has stabilized.
  It is intentionally about product terminology, not banning React as an
  implementation framework inside code, packages, contracts, or historical
  specs.
