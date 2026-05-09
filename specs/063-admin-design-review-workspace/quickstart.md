# Quickstart: Admin Design Review Workspace

1. Prepare the QA environment.

```bash
cp specs/063-admin-design-review-workspace/.env.qa063 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa063 && createdb -U postgres multi_agent_platform_qa063'
uv run alembic upgrade head
```

2. Seed live workspace records.

```bash
uv run python scripts/qa/seed_design_review_workspace_qa063.py
```

3. Run the API and worker.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

4. Open the workspace.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/design-reviews
```

5. Validate the backend envelope.

```bash
curl --fail --silent -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/design-reviews/bootstrap.json?tenant_id=11111111-1111-1111-1111-111111111111' | jq .
```

6. Run required validation.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/063-admin-design-review-workspace
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/063-admin-design-review-workspace/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/063-admin-design-review-workspace/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa063-after-spec
```
