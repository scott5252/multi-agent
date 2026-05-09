# Quickstart: Workflow Document Authoring Contracts And Mutation APIs

## Local QA Setup

```bash
cp specs/069-workflow-document-authoring-contracts-and-mutation-apis/.env.qa069 .env
uv sync
docker compose up -d postgres
uv run alembic upgrade head
uv run python scripts/qa/seed_local_principals.py
uv run python scripts/qa/seed_workflow_document_authoring_qa069.py
```

## API Check

```bash
source specs/069-workflow-document-authoring-contracts-and-mutation-apis/.env.qa069
curl -sS \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/workflows/drafts/$QA069_WORKFLOW_DRAFT_ID/detail.json?tenant_id=$QA069_TENANT_ID" \
  | jq '.draft.revision, .draft.document.roles | length, .draft.document.nodes | length'

curl -sS \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "Content-Type: application/json" \
  -X POST \
  --data @"$QA069_SAVE_PAYLOAD" \
  "http://127.0.0.1:8000/admin/app/workflows/drafts/$QA069_WORKFLOW_DRAFT_ID/save?tenant_id=$QA069_TENANT_ID" \
  | jq '.status, .revision, .validation.status'
```

## Browser Check

1. Start the API and React Admin app through the QA runner or local dev processes.
2. Log in with `tenant-admin-acme`.
3. Open Workflow Registry through the Admin navigation.
4. Open the seeded draft from the visible workflow row action.
5. Verify the draft page loads the complete workflow document summaries.
6. Save the draft and verify the save result reports an accepted durable revision.
7. Trigger the stale-save control and verify a stale conflict appears with safe recovery text.
8. Scan the page for protected raw markers; none should appear.

## Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/069-workflow-document-authoring-contracts-and-mutation-apis
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/069-workflow-document-authoring-contracts-and-mutation-apis/validation.yml --start-processes
docker compose up -d postgres
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa069-after-spec
```
