# Quickstart: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

## Focused Backend Validation

```bash
uv run pytest --no-cov \
  tests/integration/api/test_admin_memberships_ui.py \
  tests/integration/api/test_admin_telegram_ui.py \
  tests/integration/api/test_admin_briefing_preferences_ui.py \
  tests/integration/test_admin_react_routes.py \
  tests/contract/test_admin_react_contract.py \
  tests/unit/admin/test_channels_people_jinja_retirement.py \
  tests/unit/api/test_admin_memberships_router_edges.py \
  -q
```

Expected result: old memberships, Telegram, and briefing browser routes redirect
to React or return safe non-Jinja responses; retained APIs continue to serve
React; retired templates are absent and unreferenced.

## Frontend Validation

```bash
cd frontend/admin
npm test -- --run src/components/memberships src/components/channelTelegramBriefing src/App.test.tsx
npm run build
cd ../..
```

Expected result: React membership and channel workspaces render safe tenant,
membership, Telegram, delivery, run status, and briefing preference states.

## Manual Browser Checks

- Open `/auth/local-login?redirect_to=/admin/app/channels` and sign in as
  `platform-admin`.
- Confirm `/admin/app/channels` shows Telegram, delivery, run status, and
  briefing preference panels.
- Open `/admin/telegram?tenant_id=11111111-1111-1111-1111-111111111111` and
  confirm it redirects to React channels with `panel=telegram`.
- Open `/admin/briefing-preferences?tenant_id=11111111-1111-1111-1111-111111111111`
  and confirm it redirects to React channels with `panel=briefing`.
- Open `/admin/memberships?tenant_id=11111111-1111-1111-1111-111111111111` and
  confirm it redirects to `/admin/app/memberships`.
- Create a Telegram link token through React and confirm raw token visibility is
  creation-only.
- Save and export briefing preferences and confirm UI shows metadata and safe
  summaries only.
- Try a cross-tenant membership, Telegram, and briefing route and confirm the
  backend fails closed.
- Search browser text and QA evidence for raw Auth0 subjects, raw link tokens
  after creation, full Telegram ids, private messages, private preference
  values, raw imports, stack traces, and unauthorized tenant labels.

## Final Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/045-channels-memberships-access-telegram-and-briefing-full-react-parity
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/045-channels-memberships-access-telegram-and-briefing-full-react-parity/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/045-channels-memberships-access-telegram-and-briefing-full-react-parity/validation.yml --start-processes
```

Expected result: QA docs, full quality gates, coverage, and Playwright pass
before advancing to Spec 046.
