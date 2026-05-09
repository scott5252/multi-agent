# Quickstart: Durable Agent Interaction Evidence And Replay Graph

## Local QA Setup

```bash
cp specs/068-durable-agent-interaction-evidence-and-replay-graph/.env.qa068 .env
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/qa/seed_local_principals.py
uv run python scripts/qa/seed_runtime_interaction_evidence_qa068.py
```

## API Check

```bash
source specs/068-durable-agent-interaction-evidence-and-replay-graph/.env.qa068
curl -sS \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/runs/$QA068_WORKFLOW_RUN_ID/agent-graph?tenant_id=$QA068_TENANT_ID" \
  | jq '.provenance.evidence_counts, [.edges[].references[]? | select(.reference_type == "interaction_evidence")] | length'
```

## Browser Check

1. Start the API and React admin app through the QA runner or local dev processes.
2. Log in with `tenant-admin-acme`.
3. Open `/admin/app/operations?run_id=$QA068_WORKFLOW_RUN_ID`.
4. Verify the runtime graph panel shows replay references on communication edges.
5. Select an edge and verify safe replay summaries, statuses, and timestamps appear.
6. Scan the page for protected raw markers; none should appear.

## Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/068-durable-agent-interaction-evidence-and-replay-graph
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/graphical-ui-roadmap/068-durable-agent-interaction-evidence-and-replay-graph/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/graphical-ui-roadmap/068-durable-agent-interaction-evidence-and-replay-graph/validation.yml --start-processes
docker compose up -d postgres
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa068-after-spec
```
