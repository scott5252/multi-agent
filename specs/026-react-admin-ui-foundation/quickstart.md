# Quickstart: React Admin UI Foundation

## Prerequisites

- Python dependencies installed with `uv sync`
- Node.js `>=20.19.0 <26`
- Docker/PostgreSQL available for QA validation
- No real Auth0, Telegram, model provider, credential, connector, or external
  tool calls are required for local validation

## Build And Test Backend

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py
```

## Build And Test Frontend

```bash
cd frontend/admin
npm install
npm run lint
npm run typecheck
npm run test
npm run build
```

## Generate Browser Contracts

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Use the non-check mode only when intentionally refreshing generated
`frontend/admin/src/api/generated/reactAdminApi.ts` from backend schemas.

## Run Local Admin App

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Open `http://127.0.0.1:8000/admin/app` with an authorized admin principal. The
page should show the minimal React shell, safe principal summary, active scope,
available scope links, app version, and authorized fallback links to existing
Jinja admin pages.

For frontend-only iteration:

```bash
cd frontend/admin
npm run dev
```

The Vite dev server proxies backend bootstrap requests to the FastAPI app. This
is for local development only; production-like validation uses built assets
served by FastAPI under `/admin/static/react`.

## Required QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/026-react-admin-ui-foundation
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml --start-processes
```

The QA manifest must use only `multi_agent_platform_qa026` and the Spec 026
`.env.qa026` file.

## Manual Reviewer Notes

- Verify `AUTH_MODE=local_principal` browser smoke can open `/admin/app`.
- Verify Auth0-backed route tests exercise principal claim resolution and
  denied access without live Auth0 calls.
- Verify existing `/admin` Jinja routes remain directly accessible.
- Verify bootstrap JSON contains safe summaries only and omits raw tokens,
  claims, secrets, prompts, completions, memory content, provider payloads,
  tool payloads, and stack traces.
