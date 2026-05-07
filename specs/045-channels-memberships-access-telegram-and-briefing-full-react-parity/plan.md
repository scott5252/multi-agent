# Implementation Plan: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

**Branch**: `codex/045-channels-memberships-access-telegram-and-briefing-full-react-parity`  
**Spec**: `specs/045-channels-memberships-access-telegram-and-briefing-full-react-parity/spec.md`  
**Created**: 2026-05-07

## Summary

Spec 045 retires the remaining domain Jinja browser templates for memberships,
Telegram configuration, and briefing preferences by converting old browser GET
and form-post routes to React redirects or safe retained API behavior. Existing
React workspaces from Specs 034 and 036 already provide `/admin/app/memberships`
and `/admin/app/channels`; this spec closes legacy browser parity gaps, updates
navigation and saved-filter destinations, deletes bounded templates, and proves
redaction plus tenant isolation with full QA.

## Technical Context

- FastAPI routers: `admin_memberships.py`, `admin_telegram.py`, and
  `admin_briefing_preferences.py`.
- React host/routes: `/admin/app/memberships`, `/admin/app/channels`, and
  `/admin/app/channels/runs/{workflow_run_id}`.
- Retained APIs: `/admin/memberships/api/*`, `/admin/telegram/api/*`, and
  `/admin/briefing-preferences/api/*`.
- React services: `admin/memberships/react_memberships.py` and
  `admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- Templates eligible for deletion after tests:
  `templates/memberships/index.html`, `templates/telegram/index.html`, and
  `templates/briefing_preferences/index.html`.
- Jinja infrastructure and admin shell templates remain for Spec 047.

## Constitution Check

- **Tenant Isolation**: PASS. Old routes continue to resolve principals and
  scopes through existing dependencies and services before redirecting.
- **Audit And Redaction**: PASS. Mutation services keep audit references and
  safe summaries; raw tokens and private values are not persisted in redirects.
- **No Live External Calls**: PASS. Telegram validation remains mocked-safe in
  local and CI validation.
- **Backend-Owned Contracts**: PASS. React continues to consume generated
  Pydantic-backed JSON contracts.
- **No Unbounded Deletion**: PASS. Only three domain templates are deleted; Jinja
  dependencies and shell templates stay until Spec 047.

## Project Structure

```text
src/multi_agent_platform/api/routers/
- admin_memberships.py
- admin_telegram.py
- admin_briefing_preferences.py

src/multi_agent_platform/api/ui/
- admin_console.py

src/multi_agent_platform/web_admin/templates/
- memberships/index.html
- telegram/index.html
- briefing_preferences/index.html

frontend/admin/src/components/
- memberships/
- channelTelegramBriefing/

tests/
- integration/api/test_admin_memberships_ui.py
- integration/api/test_admin_telegram_ui.py
- integration/api/test_admin_briefing_preferences_ui.py
- integration/test_admin_react_routes.py
- unit/admin/test_channels_people_jinja_retirement.py
```

## Phase 1: Legacy Route Tests

Add or update tests so every old browser route is covered before deletion.
Tests must assert:

- Browser GET routes return 303 redirects to React.
- Safe query params such as `tenant_id`, `q`, `status`, `alias_id`,
  `principal_id`, `membership_id`, `role_grant_id`, `saved_filter_id`, and
  `panel` survive when safe.
- Form-post routes execute existing service behavior when needed and redirect
  to React.
- Cross-tenant or unauthorized requests fail closed.
- Link-token raw values are visible only on immediate creation responses.

## Phase 2: Router Conversion

Convert `admin_memberships.py`, `admin_telegram.py`, and
`admin_briefing_preferences.py` browser handlers:

- Remove `TemplateResponse` calls from the converted browser paths.
- Keep `/api/*` handlers unchanged except for safe destination links.
- Add redirect helpers with allowlisted query keys.
- Keep old form actions as compatibility handlers around existing services.
- Return safe non-Jinja errors when a redirect would leak unauthorized existence.

## Phase 3: React Destination And Navigation Updates

Update admin shell navigation, saved-filter profiles, migration ledger notes,
docs, and old links so membership destinations point to `/admin/app/memberships`
and Telegram/briefing destinations point to `/admin/app/channels`.

Regenerate TypeScript contracts when backend route metadata changes.

## Phase 4: Template Deletion

Delete only:

- `src/multi_agent_platform/web_admin/templates/memberships/index.html`
- `src/multi_agent_platform/web_admin/templates/telegram/index.html`
- `src/multi_agent_platform/web_admin/templates/briefing_preferences/index.html`

Add a scanner test that fails if converted routers mention these templates,
`TemplateResponse`, `Jinja2Templates`, or `workflow_ui_templates`.

## Phase 5: QA And Validation

Create `.env.qa045`, `qa045.md`, `qa045_ui.md`, `qa045_user_guide.md`, and
`pr_notes.md`.

Patch the generated Playwright manifest to log in through local-principal auth
and open `/admin/app/channels`.

Run:

- QA document validation.
- Focused backend, contract, unit, and performance tests.
- Frontend membership/channel tests plus `App.test.tsx`.
- Generated TypeScript contract check.
- Full Spec QA.
- Playwright UI validation.

## Risks

- Old form-post routes may be relied on by docs or saved browser forms; preserve
  compatibility by redirecting after existing service behavior.
- Link-token evidence can leak if tests assert raw token values after creation;
  scanner and docs must keep token visibility bounded.
- Briefing export/import routes can leak private preference payloads; React and
  old compatibility routes should expose metadata and safe summaries only.
- Tenant membership mutations are high-risk; route tests must include platform,
  tenant admin, tenant user, unauthorized, and cross-tenant principals.
