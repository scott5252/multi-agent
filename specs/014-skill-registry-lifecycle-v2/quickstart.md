# Quickstart: Skill Registry Lifecycle Browser Workflows

This quickstart describes the target V2 reviewer flow. API endpoints remain
available for automation, diagnostics, and integration tests, but
non-technical QA uses the browser for every primary skill lifecycle action.

## Prerequisites

```bash
uv sync
uv run alembic upgrade head
```

Use local-principal admin test mode for reviewer flows unless Auth0 test
credentials are available.

## Start The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

When smoke-test workers are enabled, run the worker process in a second
terminal:

```bash
uv run python -m multi_agent_platform.workers.main
```

## Platform Admin Browser Flow

1. Open `/auth/local-login?redirect_to=/admin/skill-registry/ui/packages` and
   sign in as the platform admin.
2. Open `/admin/skill-registry/ui/packages`.
3. Choose the create package action and submit slug, display name,
   description, steward/owner, lifecycle intent, and safe documentation
   summary.
4. From the package detail page, open the manifest candidate form.
5. Paste or upload a YAML or JSON manifest and submit it.
6. Confirm the page shows a safe manifest summary, candidate revision, digest,
   parse/schema status, and no raw manifest payload.
7. Run candidate validation from the browser.
8. Confirm blocking, warning, and informational findings render inline with
   affected areas and safe recovery guidance.
9. Confirm publish is unavailable or refused while blocking findings, stale
   validation, duplicate version, or lifecycle blockers exist.
10. Correct the candidate through the browser and validate again.
11. Publish the immutable version from the browser after validation passes.
12. Open the version detail page and confirm pinned semantic version,
   manifest digest, artifact digest, safe manifest summary, validation
   evidence, provenance, smoke-test expectations, and redaction notice.
13. Open the tenant grant form, select Acme, submit the grant, and confirm the
   current availability list.

## Tenant Admin Browser Flow

1. Open `/auth/local-login?redirect_to=/admin/skill-registry/ui/available-versions?tenant_id=<acme-tenant-id>`
   and sign in as the Acme tenant admin.
2. Confirm the granted version appears on the available skill versions page
   with safe package summary, credential requirements, smoke-test
   expectations, compatibility, and install action.
3. Install the granted immutable version from the browser.
4. Confirm the installation detail page shows exact package version,
   installation version, revision token, readiness state, credential status,
   smoke-test status, findings, and binding eligibility entry point.
5. Open credential reference configuration.
6. Select tenant-authorized existing credential references or delegated
   credential metadata from picker controls. Do not enter raw secrets,
   provider tokens, or arbitrary reference identifiers.
7. Save credential configuration and confirm readiness findings update with
   satisfied, missing, revoked, unauthorized, wrong-scope, incompatible, or
   blocked statuses as applicable.
8. Run or rerun declared smoke tests from the browser.
9. Confirm the browser shows queued/running status immediately, then final
   passed, failed, skipped, blocked, or timeout evidence through refresh or
   polling.
10. Confirm the installation becomes ready only when required credentials,
   compatibility checks, policy checks, and required smoke tests satisfy
   policy.

## Binding Eligibility Browser Flow

1. From installation detail, open the binding eligibility preview panel.
2. Select an authorized profile or workflow-role context.
3. Preview eligibility from the browser.
4. Confirm allowed results include exact installation version, package
   version, readiness state, and safe policy summary.
5. Confirm denied results include redacted readiness, policy, tenant
   authorization, action category, credential, quarantine, or compatibility
   reasons with recovery guidance.
6. Confirm the page states that existing bindings remain pinned until an
   authorized admin explicitly changes them.

## Stale Revision Browser Check

1. Open the same candidate, grant, or installation credential form in two
   browser sessions.
2. Submit a valid change in the first session.
3. Submit a change from the stale second session.
4. Confirm the stale submission shows an in-browser conflict, applies no state
   change, records safe audit evidence, and offers reload-latest and retry
   actions.

## Tenant Isolation Browser Check

1. Sign in as Globex tenant admin.
2. Open the available skill versions page for Globex.
3. Confirm Acme-only package versions are absent.
4. Attempt direct links to Acme-only version, installation, credential,
   smoke-test evidence, binding preview, or audit pages.
5. Confirm cross-tenant attempts render absent/not found without existence
   hints.
6. Confirm same-tenant role failures, if tested with a lower-privilege
   principal, render access denied.

## Redaction Evidence

For each major screenshot, verify that the page omits:

- raw package payloads,
- raw credential values,
- provider tokens,
- unsafe documentation,
- unsafe fixture payloads,
- raw validation input,
- raw smoke-test logs,
- cross-tenant data.

## Automated Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Targeted suites for implementation:

```bash
uv run pytest tests/unit/api/test_skill_registry_ui_models.py
uv run pytest tests/unit/api/test_admin_skill_registry_router.py
uv run pytest tests/integration/api/test_admin_skill_registry_ui.py
uv run pytest tests/docs/test_skill_registry_docs.py
```

## Required QA UI Evidence

The final `qa014_ui.md` must use browser actions for package creation,
manifest entry or upload, candidate validation, publication, tenant grants,
tenant discovery, tenant installation, credential reference configuration,
smoke-test actions, readiness review, binding eligibility preview, stale
revision conflict recovery, authorized Acme visibility, unauthorized Globex
absence/denial, and redaction checks.

Terminal commands in that guide are allowed only for environment setup, server
startup, diagnostics, and automated evidence collection. They must not use
curl, SQL, or direct API calls for primary feature actions.
