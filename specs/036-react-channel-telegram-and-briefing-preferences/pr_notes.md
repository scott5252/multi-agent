# PR Notes: Spec 036 - React Channel, Telegram, And Briefing Preferences

## Summary

- Adds the React `/admin/app/channels` workspace for channel readiness, Telegram configuration, alias management, one-time link-token handling, linked identity summaries, delivery diagnostics, safe run status, and Daily Intelligence Briefing preferences.
- Adds backend-owned safe Pydantic contracts, deterministic QA036 projections, protected route surfaces, generated TypeScript contracts, client helpers, React panels, focused tests, QA docs, and validation manifest coverage.
- Preserves existing Jinja fallbacks until Spec 037 migration hardening and retirement checks.

## Reviewer Focus

- Confirm tenant-admin Acme dashboards exclude Globex data.
- Confirm tenant users can manage preferences but do not see tenant-wide alias administration.
- Confirm link-token creation is visible once and sanitized before any saved QA evidence.
- Confirm admin preference summaries show counts, masked hints, safe references, revision metadata, and artifact references only.
- Confirm delivery diagnostics and run status links do not expose raw run inputs, prompts, completions, private messages, run results, or raw tool payloads.

## Validation Evidence

- QA guide: `specs/036-react-channel-telegram-and-briefing-preferences/qa036.md`
- UI walkthrough: `specs/036-react-channel-telegram-and-briefing-preferences/qa036_ui.md`
- User guide: `specs/036-react-channel-telegram-and-briefing-preferences/qa036_user_guide.md`
- Environment: `specs/036-react-channel-telegram-and-briefing-preferences/.env.qa036`
- Manifest: `specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml`

## Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/036-react-channel-telegram-and-briefing-preferences
uv run python scripts/frontend/generate_admin_react_types.py --check
uv run pytest --no-cov tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
cd frontend/admin && npm run typecheck && npm run test && npm run build && cd ../..
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml --start-processes
```

## Known Limits

- Local QA uses deterministic projections and mock-safe Telegram delivery state.
- Scheduled briefing time is profile metadata only; it does not create a scheduler.
- Safe run status is intentionally not a raw run inspection page.
