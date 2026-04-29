# QA014 UI: Skill Registry And Installation Lifecycle

## Goal

Validate Spec 014 through the server-rendered admin UI. The walkthrough covers
platform package review, tenant installation review, safe redaction notices,
readiness findings, binding eligibility status, and browser-first reviewer
evidence for `qa014`.

## How To Use This Guide

Use Terminal A for the API server and Terminal B for setup and automated
evidence. Use one browser window for platform checks and one browser window or
private tab for tenant checks.

Record screenshots or reviewer notes for every screen. The expected UUIDs and
digests may differ from your run, but the visible sections and safety language
should match.

## Environment Setup

Step 1 - Copy the environment.

```bash
cp specs/014-skill-registry-lifecycle/.env.qa014 .env
```

Expected: no output.

What is happening: the app is pointed at local-principal auth, the QA014
database, fake `qa014/` secret references, and `.data/qa014-artifacts`.

Why this matters: browser checks must not touch default local data or real
credential material.

Step 2 - Install dependencies.

```bash
uv sync
```

Expected: command completes without an error.

What is happening: the local Python environment is prepared.

Why this matters: the server and templates need the current dependency set.

Step 3 - Reset the database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa014 && createdb -U postgres multi_agent_platform_qa014'
uv run alembic upgrade head
```

Expected: migrations complete without an error.

What is happening: PostgreSQL receives the current schema, including
`skill_packages`, `skill_package_versions`, `skill_installations`, and
`skill_audit_records`.

Why this matters: the admin pages need persisted lifecycle tables.

Step 4 - Seed tenants.

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa014 -v ON_ERROR_STOP=1 <<'SQL'
INSERT INTO tenants (
  tenant_id, slug, display_name, status, created_at, updated_at
) VALUES
  ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (tenant_id) DO UPDATE SET
  slug = EXCLUDED.slug,
  display_name = EXCLUDED.display_name,
  status = EXCLUDED.status,
  updated_at = CURRENT_TIMESTAMP;
SQL
```

Expected: PostgreSQL reports two inserted or updated rows.

What is happening: Acme and Globex become valid admin-shell tenant scopes.

Why this matters: the UI pass checks tenant scope and cross-tenant behavior.

Step 5 - Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected: the server listens on `http://127.0.0.1:8000`.

What is happening: FastAPI serves the admin shell and skill registry pages.

Why this matters: browser checks use the live server-rendered pages.

## Browser Walkthrough

Step 1 - Log in as platform admin.

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/skill-registry/ui/packages
```

Expected: the local login page shows `Platform Admin`.

What is happening: the browser begins a platform-scope session.

Why this matters: package publication and tenant grants are platform actions.

Step 2 - Open the package list.

Navigate to:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/packages
```

Expected: the page title is `Skill Registry`; the page includes a redaction
notice and a package table.

What is happening: the admin shell renders the package list surface.

Why this matters: reviewers should see safe empty states before package data
exists.

Step 3 - Create package data through the API helper.

Run in Terminal B:

```bash
export BASE_URL=http://127.0.0.1:8000
curl -sS -X POST "$BASE_URL/admin/skill-registry/packages" \
  -H 'X-Local-Principal: platform-admin' -H 'Content-Type: application/json' \
  -d '{"slug":"calendar-assistant","display_name":"Calendar Assistant","description":"Safe calendar skill.","owner_principal_id":"platform-admin"}' \
  | tee /tmp/qa014-ui-package.json
```

Expected: JSON contains `calendar-assistant`.

What is happening: the current implementation exposes package creation through
the JSON route and reflects it in the in-process UI state.

Why this matters: the UI package list can be reviewed without manual database
edits.

Step 4 - Refresh the package list.

Expected: the `calendar-assistant` row appears with state `approved`.

What is happening: the package list now shows a platform package lineage root.

Why this matters: package identity is visible without exposing package
payloads.

Step 5 - Open package detail.

Navigate to:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/packages/calendar-assistant
```

Expected: the detail page shows package slug, name, lifecycle state,
description, a versions section, and an audit timeline section.

What is happening: the page displays safe lineage information.

Why this matters: platform admins need package history and current state.

Step 6 - Validate and publish package data through the API helper.

Use the manifest setup from `qa014.md`, then run:

```bash
curl -sS -X POST "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions" \
  -H 'X-Local-Principal: platform-admin' -H 'Content-Type: application/json' \
  -d @/tmp/qa014-manifest.json | tee /tmp/qa014-ui-version.json
```

Expected: JSON contains `1.2.3`, `sha256:`, and `passed`.

What is happening: a published immutable version is created.

Why this matters: version detail pages should show pinned provenance.

Step 7 - Refresh package detail.

Expected: the versions table shows `1.2.3`, validation status `passed`, a
manifest digest, and an artifact digest.

What is happening: package detail now includes version provenance.

Why this matters: reviewers can confirm immutable identifiers are visible.

Step 8 - Open version detail.

Navigate to:

```text
http://127.0.0.1:8000/admin/skill-registry/ui/packages/calendar-assistant/versions/1.2.3
```

Expected: version provenance shows semantic version, lifecycle state,
manifest digest, artifact digest, runtime blocked state, quarantine state, and
validation findings.

What is happening: the UI displays safe package-version evidence.

Why this matters: raw package contents are not required for review.

Step 9 - Grant Acme availability.

Run in Terminal B:

```bash
curl -sS -o /tmp/qa014-ui-grant.txt -w '%{http_code}\n' -X POST \
  "$BASE_URL/admin/skill-registry/packages/calendar-assistant/versions/1.2.3/availability" \
  -H 'X-Local-Principal: platform-admin' -H 'Content-Type: application/json' \
  -d '{"tenant_id":"11111111-1111-1111-1111-111111111111"}'
```

Expected: command prints `204`.

What is happening: Acme is authorized for new installation.

Why this matters: tenant discovery should be scoped.

Step 10 - Log in as Acme tenant admin.

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/skill-registry/ui/installations?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected: choose `Acme Tenant Admin`; the browser lands on Installed Skills.

What is happening: the browser changes to tenant scope.

Why this matters: installation review is tenant-specific.

Step 11 - Review empty installation list.

Expected: the page title is `Installed Skills`; the table shows no installed
skills or only Acme scoped rows; the redaction notice is visible.

What is happening: tenant view is safe before installation.

Why this matters: cross-tenant data should not appear.

Step 12 - Create an Acme installation through the API helper.

Run in Terminal B:

```bash
curl -sS -X POST "$BASE_URL/admin/skill-registry/installations" \
  -H 'X-Local-Principal: tenant-admin-acme' -H 'Content-Type: application/json' \
  -d '{"tenant_id":"11111111-1111-1111-1111-111111111111","slug":"calendar-assistant","semantic_version":"1.2.3"}' \
  | tee /tmp/qa014-ui-installation.json
```

Expected: JSON contains `blocked` readiness.

What is happening: the tenant installation pins package version evidence.

Why this matters: missing credentials should block readiness.

Step 13 - Refresh installed skills.

Expected: the row shows `calendar-assistant`, package version `1.2.3`,
installation version `1`, readiness `blocked`, and binding `denied`.

What is happening: the tenant list displays actionable lifecycle state.

Why this matters: tenant admins can identify blocked installations quickly.

Step 14 - Open installation detail.

Run:

```bash
export QA014_UI_INSTALLATION_ID=$(jq -r '.installation_id' /tmp/qa014-ui-installation.json)
printf 'http://127.0.0.1:8000/admin/skill-registry/ui/installations/%s\n' "$QA014_UI_INSTALLATION_ID"
```

Expected: command prints a URL. Open it in the browser.

What is happening: the reviewer navigates to the exact installed skill.

Why this matters: detail pages must expose pinned evidence and findings.

Step 15 - Review installation detail.

Expected: the page shows tenant id, skill version, installation version,
revision token, manifest digest, artifact digest, readiness section, smoke
tests section, binding eligibility section, and audit timeline section.

What is happening: the installation detail page displays safe summaries only.

Why this matters: raw credential fields must not be present.

Step 16 - Configure credential reference.

Run in Terminal B:

```bash
export QA014_UI_REVISION_TOKEN=$(jq -r '.revision_token' /tmp/qa014-ui-installation.json)
curl -sS -X POST "$BASE_URL/admin/skill-registry/installations/$QA014_UI_INSTALLATION_ID/credentials" \
  -H 'X-Local-Principal: tenant-admin-acme' -H 'Content-Type: application/json' \
  -d "{\"revision_token\":\"$QA014_UI_REVISION_TOKEN\",\"credentials\":[{\"requirement_key\":\"calendar-oauth\",\"credential_kind\":\"delegated_credential\",\"reference_id\":\"delegated-calendar-acme\",\"status\":\"ready\",\"safe_summary\":{\"scope\":\"calendar.readonly\"}}]}" \
  | tee /tmp/qa014-ui-configured.json
```

Expected: JSON contains `ready` readiness.

What is happening: credential readiness is satisfied by reference metadata.

Why this matters: no raw credential entry fields are used.

Step 17 - Refresh installation detail.

Expected: readiness is `ready`, credentials are `ready`, and binding
eligibility is `eligible`.

What is happening: the UI reflects recomputed readiness.

Why this matters: tenant admins can see when a skill can be bound.

Step 18 - Screenshot and evidence notes.

Expected: reviewer evidence includes screenshots or notes for package list,
package detail, version detail, installation list, installation detail, and
redaction notices.

What is happening: browser-first evidence is captured.

Why this matters: reviewers can validate operator experience and safety
language.

## Required Automated Evidence

Run Ruff.

```bash
uv run ruff check .
```

Expected: command exits with status `0`.

Run format check.

```bash
uv run ruff format --check .
```

Expected: command exits with status `0`.

Run mypy.

```bash
uv run mypy src
```

Expected: command exits with status `0`.

Run full coverage.

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: command exits with status `0` before merge.

## UI Evidence Checklist

- Screenshot or reviewer note for local login.
- Screenshot or reviewer note for package list.
- Screenshot or reviewer note for package detail.
- Screenshot or reviewer note for version detail.
- Screenshot or reviewer note for Acme installation list.
- Screenshot or reviewer note for installation detail.
- Screenshot or reviewer note that raw credential fields are absent.
- Screenshot or reviewer note that redaction notices are visible.
- Screenshot or reviewer note that binding eligibility changes after
  credential reference configuration.

## Acceptance Notes Template

- Browser and date:
- Platform principal used:
- Tenant principal used:
- Package list result:
- Version detail result:
- Tenant installation result:
- Credential reference result:
- Binding eligibility result:
- Redaction review:
- Automated evidence:

## Troubleshooting

- If the login page does not show QA principals, recopy `.env.qa014` to `.env`
  and restart the API.
- If the admin shell denies navigation, confirm tenant scope query is present
  for installation pages.
- If package rows disappear after reload, confirm the API server process did
  not restart and clear in-memory helper state.
- If UI checks need durable state, seed rows directly with the SQL checks from
  `qa014.md`.
- If a page returns 503, inspect API logs for admin-shell audit persistence.
- If a redaction notice is missing, capture the page and inspect the template.

## Related Files

- `specs/014-skill-registry-lifecycle/qa014.md`
- `specs/014-skill-registry-lifecycle/.env.qa014`
- `src/multi_agent_platform/api/routers/admin_skill_registry.py`
- `src/multi_agent_platform/api/ui/skill_registry.py`
- `src/multi_agent_platform/web_admin/templates/skill_registry/package_list.html`
- `src/multi_agent_platform/web_admin/templates/skill_registry/package_detail.html`
- `src/multi_agent_platform/web_admin/templates/skill_registry/package_version_detail.html`
- `src/multi_agent_platform/web_admin/templates/skill_registry/installation_list.html`
- `src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html`
