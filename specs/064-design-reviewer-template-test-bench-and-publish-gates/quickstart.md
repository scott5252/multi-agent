# Quickstart: Design Reviewer Template, Test Bench, And Publish Gates

## Local QA Setup

1. Start PostgreSQL and apply migrations.

```bash
docker compose up -d postgres
uv run alembic upgrade head
```

2. Seed local tenants and local-principal admin state.

```bash
uv run python scripts/qa/seed_local_principals.py
```

3. Install the council template in the QA064 database through the dedicated QA
   seed script.

```bash
uv run python scripts/qa/seed_design_review_template_qa064.py
```

4. Verify backend state, evidence freshness, denial behavior, and redaction.

```bash
uv run python scripts/qa/verify_design_review_template_qa064.py
```

5. Run the Spec Kit validation manifest.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/064-design-reviewer-template-test-bench-and-publish-gates/validation.yml
```

6. Run the Admin workspace Playwright flow.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/064-design-reviewer-template-test-bench-and-publish-gates/validation.yml --start-processes
```

7. Run the full curl regression.

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa064-after-spec
```

## Expected Results

- Template install action is idempotent and tenant-scoped.
- Workflow draft contains lead, reviewer, quorum, synthesis, and handoff roles.
- Required Test Bench suite exists and targets the workflow draft.
- Latest passing evidence targets the current draft revision.
- Publish gate reports ready only when evidence is current and passing.
- Admin workspace shows live template readiness and no fabricated sessions.
- Cross-tenant requests fail closed with safe problem details.
- QA artifacts and screenshots contain no raw prompts, completions, secrets,
  provider payloads, private channel messages, memory contents, unauthorized
  payloads, or raw external tool payloads.
