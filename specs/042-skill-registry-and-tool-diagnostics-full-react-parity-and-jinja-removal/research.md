# Research: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

## Decision: Extend The Spec 032 React Skill Lifecycle Workspace

**Rationale**: Spec 032 already introduced backend-owned skill lifecycle builders, schemas, React components, mutation helpers, and Playwright coverage for `/admin/app/skills`. Extending that surface keeps authorization, tenant scope, manifest safety, credential readiness, smoke evidence, and diagnostics decisions on the backend while minimizing UI drift.

**Alternatives considered**:

- Build a new React skill registry workspace: rejected because it would duplicate existing routes and contracts.
- Keep Jinja pages for missing details: rejected because Spec 042 requires deletion-grade parity for skill-owned browser routes.

## Decision: Use Stable React Skill Child Routes For Direct Links

**Rationale**: Old skill URLs carry package slugs, versions, installation ids, tenant ids, conflict state, filters, and safe return intent. Stable React child routes under `/admin/app/skills` let old URLs redirect to one non-Jinja host while preserving context.

**Alternatives considered**:

- Redirect every old skill URL to `/admin/app/skills`: rejected because reviewers and operators would lose direct-link context.
- Retain old Jinja pages as permanent fallbacks: rejected for skill-owned pages once route parity evidence passes.

## Decision: Preserve Upload-Over-Paste Manifest Precedence

**Rationale**: Upload precedence is already documented by the React skill lifecycle contract and avoids ambiguous dual-input behavior. The selected source can be recorded safely without returning raw manifest text.

**Alternatives considered**:

- Reject dual-input submissions: rejected because it would be a stricter behavior change than needed for parity.
- Prefer paste over upload: rejected because uploaded fixtures are easier to audit deterministically in QA.

## Decision: Never Re-Render Raw Manifests After Submit

**Rationale**: Skill manifests can contain endpoint examples, connector payload shapes, credential names, and other sensitive operational details. React should receive safe summaries, metadata, validation findings, fingerprints, revision tokens, and artifact references only.

**Alternatives considered**:

- Echo sanitized JSON snippets: rejected because sanitization drift is a high-risk redaction surface.
- Store manifest text in browser state for editing: rejected because Spec 042 is about safe parity, not a raw manifest editor.

## Decision: Keep Refresh Actions Explicit And Mocked-Safe

**Rationale**: Smoke-test refreshes and SkillExecutionGateway diagnostics can look like external side effects. Making them explicit user actions and deterministic mocked-safe checks in local/CI preserves testability and avoids hidden connector calls.

**Alternatives considered**:

- Auto-refresh diagnostics on page load: rejected because it creates hidden work and unreliable QA.
- Use live connectors in validation: rejected because the roadmap forbids unapproved live provider, credential, connector, and external tool calls.

## Decision: Convert Old Browser Routes Before Template Deletion

**Rationale**: `admin_skill_registry.py` and `admin_skill_execution.py` currently contain TemplateResponse-backed browser pages and form routes. GET routes should redirect or return safe non-Jinja problems after React parity is available. Legacy form POST routes should either execute existing service behavior and redirect to React or return safe mutation/problem responses.

**Alternatives considered**:

- Delete routers wholesale: rejected because JSON/API routes and service-backed form compatibility are still needed.
- Remove global Jinja infrastructure now: rejected because later specs still own other Jinja domains and Spec 047 owns infrastructure decommissioning.

## Decision: Delete Skill-Owned Templates Only With Scanner And Route Evidence

**Rationale**: Templates under `skill_registry/` and `skill_execution/diagnostics.html` are in active scope. They can be deleted only after React contracts, route tests, redaction checks, QA docs, Playwright, and inventory evidence prove parity. Shared shell templates and other domain templates remain for later specs.

**Alternatives considered**:

- Delete all remaining Jinja templates now: rejected because Specs 043-047 still own other domains and global infrastructure.
- Retain skill templates with a broad blocker: rejected unless a specific route/helper lacks deletion-grade parity evidence.
