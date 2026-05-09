# Quickstart: React Agent Graph Viewer For Workflow Drafts And Versions

## Prerequisites

```bash
cp specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/.env.qa066 .env
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa066 && createdb -U postgres multi_agent_platform_qa066'
uv sync
uv run alembic upgrade head
```

## Generate Contracts

```bash
uv run python scripts/frontend/generate_admin_react_types.py
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Expected: `frontend/admin/src/api/generated/reactAdminApi.ts` includes `AgentCommunicationGraph` and related graph types.

## Run Focused Frontend Checks

```bash
npm --prefix frontend/admin test -- AgentGraphPanel WorkflowBuilderPage
npm --prefix frontend/admin run typecheck
npm --prefix frontend/admin run build
```

Expected: component rendering, strict TypeScript, and Vite build pass.

## Run Backend And Spec QA

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/graphical-ui-roadmap/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/validation.yml
```

Expected: QA docs and Spec QA pass.

## Run Browser Validation

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/validation.yml --start-processes
```

Expected: Playwright captures desktop and mobile graph viewer evidence under `output/playwright/qa066_ui`.

## Run Curl Regression

```bash
docker compose up -d postgres
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa066-after-spec
```

Expected: sequential curl regression passes with the Spec 065 agent-graph routes still covered.
