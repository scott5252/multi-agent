# Quickstart: Design Review Coordinator And Iteration Loop

## Setup

```bash
cp specs/062-design-review-coordinator-and-iteration-loop/.env.qa062 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa062 && createdb -U postgres multi_agent_platform_qa062'
uv run alembic upgrade head
```

## Seed

```bash
uv run python scripts/qa/seed_design_review_coordinator_qa062.py
```

## Run API And Worker

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
uv run python -m multi_agent_platform.workers.main
```

## Verify

```bash
uv run python scripts/qa/verify_design_review_coordinator_qa062.py
```

## Required Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/062-design-review-coordinator-and-iteration-loop
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa062-after-spec
```
