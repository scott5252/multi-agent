# Testing Instructions: User Briefing Preferences And Context

## Focused Tests

```bash
uv run pytest --no-cov \
  tests/contract/test_briefing_preferences_contract.py \
  tests/docs/test_briefing_preferences_docs.py \
  tests/unit/auth/test_briefing_preferences_policy.py \
  tests/unit/admin/briefing_preferences/test_briefing_preference_service.py \
  tests/unit/db/test_briefing_preferences_repository.py \
  tests/integration/api/test_admin_briefing_preferences_api.py \
  tests/integration/api/test_admin_briefing_preferences_ui.py \
  tests/integration/runtime/test_briefing_preference_resolution.py
```

## QA Scripts

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/023-user-briefing-preferences-and-context/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/023-user-briefing-preferences-and-context/validation.yml --start-processes
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Reviewer Notes

- Use only `.env.qa023` with `multi_agent_platform_qa023`.
- Do not use real Telegram, Gmail, Calendar, or provider credentials.
- Confirm safe summaries mask VIP senders and account references.
- Confirm runtime resolve includes revision id and content digest.
- Confirm Globex cannot read Acme profile data.
