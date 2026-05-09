# Quickstart: Design Review Domain Foundation

## Goal

Validate that Spec 060 adds durable tenant-scoped design review backend
contracts without live model calls, coordinator auto-launch, Admin workspace UI,
or unsafe payload exposure.

## Local Setup

1. Sync dependencies:

   ```bash
   uv sync
   ```

2. Prepare the qa060 database:

   ```bash
   cp specs/060-design-review-domain-foundation/.env.qa060 .env
   docker compose up -d postgres
   uv run alembic upgrade head
   uv run python scripts/qa/seed_design_review_qa060.py
   ```

3. Start the API:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

## Expected Behavior

- `tenant-admin-acme` can create a design review session for Acme and receives
  session metadata plus revision 1.
- Repeating the same creation request with the same idempotency key returns the
  existing session and does not duplicate revision 1.
- Session list/detail/revision/round/quorum/manual-decision/handoff contracts
  return live durable records or truthful empty/pending states.
- `tenant-admin-globex` cannot list, retrieve, or infer Acme design review
  records.
- No response includes raw prompts, completions, secrets, provider payloads,
  private channel messages, memory contents, raw artifact bodies, raw external
  tool payloads, local paths, or stack traces.

## Curl Smoke

Use the full `curl_testing.md` regression for acceptance. During development,
the route family can be smoke-tested with local-principal headers after the API
is running:

```bash
curl --fail --silent \
  -H 'X-Local-Principal: tenant-admin-acme' \
  -H 'Content-Type: application/json' \
  -X POST http://127.0.0.1:8000/admin/design-reviews/sessions \
  -d '{
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "request_summary": "Review checkout redesign for clarity and accessibility.",
    "quorum_policy_key": "four_of_five_no_blockers",
    "idempotency_key": "qa060-create-session"
  }'
```

## Validation Commands

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/060-design-review-domain-foundation
uv run pytest tests/unit/admin/design_review tests/unit/db/test_design_review_repository.py tests/contract/test_design_review_contracts.py tests/integration/api/test_admin_design_review_api.py
uv run ruff check src/multi_agent_platform/admin/design_review src/multi_agent_platform/api/routers/admin_design_review.py src/multi_agent_platform/api/schemas/design_review.py src/multi_agent_platform/db/models/design_review.py src/multi_agent_platform/db/repositories/design_review.py tests/unit/admin/design_review tests/unit/db/test_design_review_repository.py tests/contract/test_design_review_contracts.py tests/integration/api/test_admin_design_review_api.py
uv run mypy src/multi_agent_platform/admin/design_review src/multi_agent_platform/api/schemas/design_review.py src/multi_agent_platform/db/repositories/design_review.py
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa060-after-spec
```

## Reviewer Notes

- Confirm the implementation added a migration and did not mutate existing
  workflow, runtime, provider, prompt, test-bench, or Admin workspace data.
- Confirm route responses use safe summaries and artifact references only.
- Confirm Playwright smoke validates OpenAPI/health route availability for
  qa060 and does not rely on a fake Design Review UI.
