# Research: Skill Registry Lifecycle Browser Workflows

## Browser-First QA Surface

**Decision**: Add server-rendered browser forms and POST handlers for every
primary lifecycle action while keeping existing JSON API endpoints available
for automation, diagnostics, and integration tests.

**Rationale**: Spec 014 already has authoritative services and APIs, but
`qa014_ui.md` still relies on curl for primary feature actions. Non-technical
platform and tenant admins need guided browser flows that reuse the same
service layer and preserve audit, authorization, idempotency, tenant scope, and
redaction behavior.

**Alternatives considered**: Removing JSON APIs was rejected because automated
tests, integrations, and diagnostics still need them. Building a separate
client-side frontend was rejected because the existing admin shell already
provides navigation, local-principal auth, templates, empty states, and scoped
admin conventions.

## Route And Handler Pattern

**Decision**: Keep browser workflows in
`src/multi_agent_platform/api/routers/admin_skill_registry.py` under
`/admin/skill-registry/ui`, using GET handlers for forms/pages and POST
handlers that call existing `SkillRegistryService` operations or repository
backed equivalents.

**Rationale**: The current router already owns both JSON APIs and HTML pages
for Spec 014, and the codebase uses server-rendered admin templates for
non-developer workflows. Shared router ownership makes it easier to keep API
and UI authorization behavior aligned while keeping QA browser paths distinct.

**Alternatives considered**: Creating a second router was rejected because it
would duplicate dependency wiring and risk drift. Calling the JSON endpoints
from templates was rejected because server-side POST handlers can validate
forms, map safe errors, and redirect/render without introducing client
JavaScript as a requirement.

## Form Models And Validation

**Decision**: Introduce typed browser form parsing/view models that normalize
HTML form fields, uploaded files, selected tenant ids, credential picker
choices, revision tokens, idempotency keys, and action reasons before mapping
to existing service/API schemas.

**Rationale**: Browser forms produce strings and file objects, while existing
service methods expect typed payloads and safe summaries. A small form layer
keeps parsing and error presentation deterministic, supports no-JS form
submits, and makes unit testing easier.

**Alternatives considered**: Parsing form dictionaries inline in route
handlers was rejected because validation/error mapping would spread across
handlers. Reusing JSON API schemas directly was retained where shapes match,
but not forced where browser forms need upload, picker, or multi-select
behavior.

## Manifest Paste And Upload

**Decision**: Accept YAML or JSON manifest text and uploads from the candidate
form, parse with structured parsers, validate against the existing v1 manifest
schema, and render only safe summaries, candidate revision, digests, parse
issues, schema issues, and validation findings.

**Rationale**: The spec requires YAML and JSON. Structured parsing avoids
ad hoc string handling, and safe rendering preserves redaction guarantees even
when a candidate includes unsafe documentation, fixtures, or accidental secret
material.

**Alternatives considered**: JSON-only forms were rejected by the clarified
requirements. Rendering raw manifest text back to the browser was rejected
because invalid or unsafe candidate input may contain data that should not be
screenshotted.

## Tenant Scope And Authorization

**Decision**: Reuse existing Auth0/local-principal dependencies and admin shell
tenant-scope behavior. Platform actions require platform admin roles. Tenant
actions require selected-tenant authorization. Cross-tenant direct links render
not found/absent states without existence hints, while same-tenant role
failures render access denied.

**Rationale**: The feature expands browser exposure, so isolation semantics
must match the existing security model exactly. Distinguishing absent
cross-tenant records from same-tenant denied records satisfies the clarified
spec and supports safer screenshots.

**Alternatives considered**: Returning 403 for all failures was rejected
because it can reveal that cross-tenant records exist. Hiding same-tenant role
failures as not found was rejected because authorized tenant operators need a
clear role/access recovery path.

## Optimistic Concurrency UX

**Decision**: Include revision tokens on mutable browser forms for manifest
candidates, grant lists, credential configuration, smoke-test/readiness
actions, and binding-related preview state. Stale submissions render a
dedicated conflict state and do not apply changes.

**Rationale**: Existing Spec 014 lifecycle rules rely on optimistic revision
checks. Browser users need a plain-language recovery path: know nothing was
changed, reload current safe state, and retry from the latest revision.

**Alternatives considered**: Long-lived locks were rejected because admins may
leave browser tabs open. Last-write-wins was rejected because it violates the
spec's stale revision guarantees and could overwrite readiness or grants.

## Credential Configuration

**Decision**: Credential configuration uses tenant-authorized picker options
for existing secret references and delegated credential links, plus predefined
safe delegated metadata fields. The final UI must not provide arbitrary
reference id text boxes or raw secret inputs.

**Rationale**: Secret hygiene requires admins to select from references that
the platform already knows are tenant-authorized, active, and safe to display.
Picker options let the UI explain missing, revoked, wrong-scope, incompatible,
or unauthorized requirements without exposing credential payloads.

**Alternatives considered**: Free-form reference id entry was rejected because
it enables guessing, typo-driven failures, and unsafe screenshots. Raw secret
entry was rejected because the registry should store only references or
delegated credential metadata.

## Smoke-Test And Readiness Evidence

**Decision**: Browser smoke-test run/rerun actions enqueue existing
smoke-test jobs and redirect or render queued/running status with refresh or
optional polling; final status pages show safe fixture identity, outcome,
last-run time, policy summary, and redacted failure reasons.

**Rationale**: Smoke tests may need external policy/tool checks and should not
block HTTP requests. Reusing jobs keeps admission, retries, breakers, fairness,
audit, and evidence storage in the existing backend.

**Alternatives considered**: Synchronous smoke-test execution in a browser
POST was rejected for latency and reliability reasons. Displaying raw logs was
rejected because they may contain unsafe fixture or credential-adjacent data.

## Redaction-Safe Rendering

**Decision**: Every page renders through safe view models and shared redaction
notices/partials. Templates omit raw package payloads, raw credential values,
provider tokens, unsafe docs, unsafe fixtures, and cross-tenant data; tests
assert those strings do not appear in rendered HTML or screenshot-oriented
fixtures.

**Rationale**: Browser-first QA increases screenshot and accidental exposure
risk. Redaction must be a template contract, not only a backend storage rule.

**Alternatives considered**: Relying on reviewer discipline was rejected.
Rendering raw data in collapsible sections was rejected because hidden DOM
content can still leak through page source, automation, or screenshots.
