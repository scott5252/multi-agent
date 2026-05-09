# Quickstart: End-To-End Custom Workflow Setup Wizard And Runtime Launch

## Local Setup

```bash
cp specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/.env.qa073 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa073 && createdb -U postgres multi_agent_platform_qa073'
uv run alembic upgrade head
```

## Run The App

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
cd frontend/admin && npm run build
```

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows
```

Choose `tenant-admin-acme`.

## Browser Path

1. Open Workflows from the Admin shell.
2. Create a workflow.
3. Open the created draft link.
4. Use `Apply three-agent starter`.
5. Save the draft.
6. Create or attach required evidence.
7. Save the evidence requirement.
8. Add a safe case and launch deterministic evidence.
9. Run validation.
10. Prepare publish and confirm publish.
11. Open runtime launch and verify the workflow id is prefilled.
12. Open Design Reviews and verify the published workflow can be selected.
13. Inspect the draft and published graph panels.

## Automated Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa073-after-spec
```
