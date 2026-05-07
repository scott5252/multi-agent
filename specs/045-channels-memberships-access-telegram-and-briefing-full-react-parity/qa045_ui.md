# QA045 UI: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

## Goal

This walkthrough verifies the browser experience for Spec 045. Reviewers should
see React memberships and React channels as the browser destinations for old
membership, Telegram, and briefing links.

The deleted Jinja pages must not render. Sensitive people, Telegram, and
briefing data must stay redacted.

## How To Use This Guide

Use this guide from a fresh checkout or after running the QA045 setup in
`qa045.md`.

Capture notes under `/tmp/qa045-*` and screenshots under
`output/playwright/qa045_ui` or `/tmp/qa045-*`.

Suggested evidence files:

1. `/tmp/qa045-memberships-screen.png`
2. `/tmp/qa045-channels-screen.png`
3. `/tmp/qa045-telegram-token-notes.txt`
4. `/tmp/qa045-briefing-screen.png`
5. `/tmp/qa045-legacy-redirect-notes.txt`

Expected: every note names the principal, source URL, destination URL, visible
page title, and reviewer decision.

What is happening: the reviewer is checking React browser behavior after Jinja
deletion.

Why this matters: Spec 045 retires people and channel pages that carry sensitive
identity, token, and preference data.

## Environment Setup

Prepare the app:

```bash
cp specs/045-channels-memberships-access-telegram-and-briefing-full-react-parity/.env.qa045 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa045 && createdb -U postgres multi_agent_platform_qa045'
uv run alembic upgrade head
mkdir -p .data/qa045-artifacts output/playwright/qa045_ui
```

Expected: `.env` uses `AUTH_MODE=local_principal` and the QA database is
`multi_agent_platform_qa045`.

What is happening: local fake principals and mock integrations are active.

Why this matters: reviewers can test Telegram and briefing flows without live
external services.

Seed tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa045 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex tenants are available.

What is happening: tenant-scoped UI checks have deterministic ids.

Why this matters: cross-tenant isolation is part of the acceptance criteria.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: `http://127.0.0.1:8000/health/live` is healthy.

What is happening: FastAPI serves the React bundle and retained JSON APIs.

Why this matters: old browser routes must redirect into this app instance.

## Browser Walkthrough

1. Open local login.

   URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels`

   Action: choose `platform-admin`.

   Expected: the browser lands on `/admin/app/channels`.

   What is happening: local-principal auth sets the review cookie.

   Why this matters: Playwright and manual checks need a principal with broad
   enough scope to see channel and membership navigation.

2. Review React channels.

   URL: `http://127.0.0.1:8000/admin/app/channels`

   Action: inspect Telegram configuration, aliases, link tokens, identities,
   delivery diagnostics, run status, and briefing preference panels.

   Expected: the page shows React channel content and no Jinja template chrome.

   What is happening: `ChannelTelegramBriefingPage` loads backend-owned React
   dashboard contracts.

   Why this matters: this is the replacement for old Telegram and briefing
   browser pages.

3. Open an old Telegram URL.

   URL: `http://127.0.0.1:8000/admin/telegram?tenant_id=11111111-1111-1111-1111-111111111111`

   Action: paste the URL in the browser.

   Expected: the destination is `/admin/app/channels` with `panel=telegram` and
   the Acme tenant id.

   What is happening: the old Telegram route authenticates and redirects.

   Why this matters: old bookmarks remain useful without rendering
   `telegram/index.html`.

4. Create a Telegram link token.

   URL: use the React link-token control or the old form route documented in
   `qa045.md`.

   Action: create one token, then refresh or list token audits.

   Expected: the raw token appears only in the immediate creation response;
   later token lists show a fingerprint or metadata only.

   What is happening: one-time token visibility is preserved without a Jinja
   page.

   Why this matters: link tokens are credential-like and must not persist in
   screenshots or summaries.

5. Review Telegram diagnostics.

   URL: `http://127.0.0.1:8000/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111&panel=telegram`

   Action: inspect readiness, webhook validation, delivery diagnostics, and
   linked identities.

   Expected: full Telegram ids and private message text are not visible.

   What is happening: diagnostics use redacted metadata.

   Why this matters: support workflows need diagnostics without exposing private
   channel identifiers.

6. Review React memberships.

   URL: `http://127.0.0.1:8000/admin/app/memberships`

   Action: inspect user directory, invitations, principal linking, role grants,
   status actions, access history, and audit.

   Expected: the page shows membership content or safe empty states in React.

   What is happening: `MembershipPage` loads the React membership dashboard.

   Why this matters: this page replaces `memberships/index.html`.

7. Open an old membership URL.

   URL: `http://127.0.0.1:8000/admin/memberships?tenant_id=11111111-1111-1111-1111-111111111111&q=reviewer`

   Action: confirm the browser redirect.

   Expected: the destination is `/admin/app/memberships` with the Acme tenant id
   and `q=reviewer`.

   What is happening: old route query state is preserved for React.

   Why this matters: saved filters and bookmarks should survive the migration.

8. Review membership redaction.

   URL: `/admin/app/memberships`

   Action: create or inspect an invitation and principal link using safe local
   fixtures.

   Expected: raw Auth0 subjects and raw email addresses are not visible beyond
   safe labels or masked email values.

   What is happening: membership service redaction remains backend-owned.

   Why this matters: people workflows are high-sensitivity admin surfaces.

9. Open an old briefing URL.

   URL: `http://127.0.0.1:8000/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111`

   Action: paste the URL in the browser.

   Expected: the destination is `/admin/app/channels` with `panel=briefing`.

   What is happening: the old briefing browser page redirects to the React
   channel workspace.

   Why this matters: `briefing_preferences/index.html` is retired.

10. Save briefing preferences.

    URL: `/admin/app/channels?tenant_id=11111111-1111-1111-1111-111111111111&panel=briefing`

    Action: save or import preference metadata through React or the old form
    compatibility route from `qa045.md`.

    Expected: the result is a safe mutation summary or redirect; private
    preference values are not exposed in admin summaries.

    What is happening: backend validation and revision checks remain in charge.

    Why this matters: React must not become the source of truth for preference
    validation or ownership.

11. Switch to `tenant-admin-acme`.

    URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels`

    Action: choose `tenant-admin-acme` and review Acme channel and briefing
    panels.

    Expected: Acme-scoped views are available according to tenant admin
    permissions.

    What is happening: local-principal tenant scope drives React API calls.

    Why this matters: tenant admins must keep safe workflows after migration.

12. Try Globex as Acme.

    URL: `/admin/app/channels?tenant_id=22222222-2222-2222-2222-222222222222`

    Action: open the URL while signed in as `tenant-admin-acme`.

    Expected: the app fails closed or shows a safe denied state without Globex
    private data.

    What is happening: backend APIs reject unauthorized tenant scope.

    Why this matters: redirects must not become cross-tenant bypasses.

## Required Automated Evidence

Run focused backend checks:

```bash
uv run pytest --no-cov tests/integration/api/test_admin_memberships_ui.py tests/integration/api/test_admin_telegram_ui.py tests/integration/api/test_admin_briefing_preferences_ui.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py tests/unit/admin/test_channels_people_jinja_retirement.py tests/unit/api/test_admin_memberships_router_edges.py -q
```

Expected: backend redirect, API, and retirement tests pass.

Run focused frontend checks:

```bash
cd frontend/admin
npm test -- --run src/components/memberships src/components/channelTelegramBriefing src/App.test.tsx
npm run build
cd ../..
```

Expected: React membership/channel tests pass and the bundle builds.

Run full quality and Playwright:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/045-channels-memberships-access-telegram-and-briefing-full-react-parity/validation.yml --start-processes
```

Expected: all checks pass and Playwright writes
`output/playwright/qa045_ui/qa045-react-ui2-smoke.png`.

## UI Evidence Checklist

- Screenshot `/tmp/qa045-channels-screen.png` shows React channels.
- Screenshot `/tmp/qa045-memberships-screen.png` shows React memberships.
- Notes `/tmp/qa045-telegram-token-notes.txt` confirm token visibility is
  creation-only.
- Notes `/tmp/qa045-legacy-redirect-notes.txt` list old membership, Telegram,
  and briefing URLs with their React destinations.
- Evidence confirms no raw Auth0 subjects, full Telegram ids, private messages,
  raw link tokens after creation, private preference values, stack traces, or
  deleted template content appears in browser UI.
- Evidence confirms Acme and Globex scopes are isolated.

## Acceptance Notes Template

```text
QA045 UI reviewer:
Platform login completed:
Channels React route reviewed:
Telegram legacy redirects reviewed:
Link-token visibility reviewed:
Membership React route reviewed:
Membership legacy redirects reviewed:
Briefing legacy redirects reviewed:
Tenant isolation reviewed:
Redaction reviewed:
Screenshots captured:
Decision:
```

Expected: every line has a reviewer note or evidence path.

What is happening: manual evidence is recorded with the automated gates.

Why this matters: final migration acceptance needs visible behavior review.

## Troubleshooting

If the React bundle looks stale, run `cd frontend/admin && npm run build` and
restart the API.

Expected: new routes and assets appear after restart.

If local login loops, clear the `map_local_principal` cookie and open
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/channels`.

Expected: choosing `platform-admin` lands on React channels.

If a deleted template renders, stop validation and run the retirement scanner.

Expected: only scanner tests reference the retired template names.

If a raw token appears after creation, stop validation and record the response
path.

Expected: persisted views show fingerprints and audit metadata only.

## Related Files

- `specs/045-channels-memberships-access-telegram-and-briefing-full-react-parity/qa045.md`
- `specs/045-channels-memberships-access-telegram-and-briefing-full-react-parity/.env.qa045`
- `src/multi_agent_platform/api/routers/admin_memberships.py`
- `src/multi_agent_platform/api/routers/admin_telegram.py`
- `src/multi_agent_platform/api/routers/admin_briefing_preferences.py`
- `frontend/admin/src/components/memberships/MembershipPage.tsx`
- `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`
- `tests/unit/admin/test_channels_people_jinja_retirement.py`
