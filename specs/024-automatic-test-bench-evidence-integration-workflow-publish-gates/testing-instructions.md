# Testing Instructions: Automatic Test Bench Evidence Integration In Workflow Publish Gates

## Focused Tests

```bash
uv run pytest --no-cov \
  tests/unit/admin/test_publish_gate.py \
  tests/unit/admin/test_workflow_builder_references.py \
  tests/unit/admin/test_workflow_registry_service.py \
  tests/integration/api/test_admin_workflow_ui.py
```

## QA Scripts

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/024-automatic-test-bench-evidence-integration-workflow-publish-gates/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/024-automatic-test-bench-evidence-integration-workflow-publish-gates/validation.yml --start-processes
```

## Full Quality Gates

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Reviewer Notes

- Use only `.env.qa024` with `multi_agent_platform_qa024`.
- Do not use real model provider, Telegram, Gmail, Calendar, or tool credentials.
- Confirm required test declarations are evaluated from repository runs, not from manual `latest_result_status` values.
- Confirm the accepted evidence is same tenant, same suite, same target type, same target id, same current draft revision, and passing.
- Confirm missing, failed, stale, wrong-target, platform-scope, and cross-tenant evidence fails closed with safe summaries.
- Confirm publish gate evidence pins contain safe ids and statuses only, without fixture payloads, transcripts, target names from denied tenants, or artifact contents.
