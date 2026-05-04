# Quickstart: Real Skill Tool Execution Connectors

## Local QA Goal

Validate that the SkillExecutionGateway can execute Daily Briefing read-only tools in mock mode, deny unsafe requests before adapter invocation, expose redacted summaries, and render the admin diagnostics page.

## Prepare Environment

```bash
uv sync
cp specs/021-real-skill-tool-execution-connectors/.env.qa021 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa021 && createdb -U postgres multi_agent_platform_qa021'
uv run alembic upgrade head
```

## Start Services

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

## Validate API Health

```bash
curl --fail --silent http://127.0.0.1:8000/health/live
curl --fail --silent http://127.0.0.1:8000/health/ready
curl --fail --silent http://127.0.0.1:8000/version
curl --fail --silent http://127.0.0.1:8000/dependencies
```

## Validate Admin Diagnostics

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/skill-execution/ui/diagnostics`.
2. Choose `platform-admin`.
3. Confirm the page title is `Skill Tool Diagnostics`.
4. Confirm calendar, Gmail, news, weather, and commute tools are listed.
5. Confirm summaries are redacted and do not expose credential values.

## Run Automated Checks

```bash
uv run pytest tests/unit/skill_execution tests/unit/runtime/test_runtime_skill_tools.py tests/contract/test_skill_execution_gateway_contract.py tests/integration/api/test_admin_skill_execution_ui.py
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## QA Scripts

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/021-real-skill-tool-execution-connectors/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/021-real-skill-tool-execution-connectors/validation.yml --start-processes
```

## Expected Evidence

- API command logs under `.data/qa021-artifacts` or `/tmp/qa021-api.log`.
- Playwright screenshots under `output/playwright/qa021_ui`.
- Manual QA guide at `specs/021-real-skill-tool-execution-connectors/qa021_user_guide.md`.
- Generated QA docs at `specs/021-real-skill-tool-execution-connectors/qa021.md` and `specs/021-real-skill-tool-execution-connectors/qa021_ui.md`.
