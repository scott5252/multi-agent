# Spec 038 - Jinja Surface Inventory And Deletion Plan: Clarify

Roadmap source: `react_ui2.md`

## Deterministic Targets

- Feature directory: `specs/038-jinja-surface-inventory-and-deletion-plan`
- Git branch: `codex/038-jinja-surface-inventory-and-deletion-plan`
- QA id: `qa038`
- QA database: `multi_agent_platform_qa038`

## Global Prompt Prefix

Use the current multi-agent platform repository context after Specs 026 through
037. React is already primary for migrated admin workspaces, but Jinja remains
as fallback. The goal of this roadmap is complete Jinja removal, not another
additive wrapper.

Preserve the constitution, specs 001 through 037, existing FastAPI domain
services, PostgreSQL source of truth, Auth0 production authentication,
AUTH_MODE=local_principal browser QA, tenant isolation, audit fail-closed
behavior, redaction rules, runtime version pinning, secret hygiene, object
storage boundaries, generated TypeScript contracts, Playwright evidence, QA
docs, and at least 90 percent relevant coverage.

React must consume backend-owned JSON contracts generated from Pydantic schemas.
Do not move authorization, tenant scoping, validation, credential readiness,
publish readiness, redaction, or audit decisions into browser-only logic.

Every spec must explicitly prove both Auth0-shaped principal behavior with
backend route tests and local-principal behavior with browser Playwright flows.
Every retired legacy route must preserve safe direct-link behavior through a
redirect, alias, documented gone response, or retained non-Jinja compatibility
handler.

Do not remove a Jinja template, route, helper, static asset, or dependency until
the spec's parity evidence shows that the React replacement covers every safe
user journey, denied state, mutation, export, filter, direct link, and error
path. Raw secrets, credential values, provider authorization headers, raw
prompts, raw completions, memory contents, raw run payloads, private channel
messages, raw tool payloads, raw test transcripts, full Telegram identifiers,
link tokens after creation, local filesystem paths, stack traces, and
unauthorized tenant labels must never appear in React UI, redirects, exports,
screenshots, QA artifacts, logs, or docs.

## Clarify Prompt

Run clarification for the Jinja inventory. Focus on inventory sources,
definition of deletion-grade parity, whether user-facing /runs pages are in
scope, whether auth/local-login is in scope, redirect status codes, deprecation
duration, evidence retention location, route naming, and whether static Vite
index.html is allowed while Jinja is not. Recommended defaults: include all
Jinja templates in the repository, include /runs and auth/local-login, preserve
old URLs through authenticated redirects where safe, require explicit reviewer
signoff before deletion, and allow Vite/static HTML because the removal target
is server-side Jinja rendering.

## Autonomous Clarification

Use the recommended defaults in the roadmap and established repo patterns for low-risk answers. Record every auto-selected answer in spec.md with `(autopilot)`. Stop for security, tenant, audit, credential, destructive data, production resource, external side-effect, irreversible migration, legacy-route retirement, dependency deletion, or approval/resume ambiguity.

## Roadmap Execution Notes

- Create one Spec Kit feature at a time. Do not run all specs in parallel.
- Do not delete templates in Spec 038. Inventory first.
- Treat `/admin/app/migration` as the operator-facing ledger until Spec 047
  replaces it with a React-only decommission summary.
- Every old browser route must be tested after its template is removed.
- Keep API routes that are still used by React. Remove only browser-rendering
  Jinja routes or convert them to JSON/redirect handlers.
- For old URLs, prefer authenticated redirects that preserve tenant id, route
  parameters, filters, saved-filter intent, and safe breadcrumbs.
- A route that cannot safely redirect must return a non-Jinja safe problem or
  documented retirement response without exposing whether unauthorized data
  exists.
- Local login, user-facing `/runs`, and the React app host are in scope for
  complete Jinja removal.
- Do not remove `jinja2` from dependencies until an import scanner and full test
  suite prove no runtime path imports it.
- The final state should describe the browser UI as React-only, not React
  primary with Jinja fallback.
