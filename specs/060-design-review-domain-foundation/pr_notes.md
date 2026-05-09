# PR Notes: Spec 060 - Design Review Domain Foundation

## Summary

Adds the durable design review domain foundation for scenario enhancement work.

The implementation introduces tenant-scoped sessions, revisions, rounds,
assignments, verdicts, quorum decisions, manual decisions, and handoff metadata.

The API exposes safe JSON contracts for create, list, detail, revision, round,
quorum, manual-decision, and handoff reads.

Manual decisions and session creation are idempotent.

Routes are registered in the auth surface policy and the FastAPI app.

## Validation

- `uv run pytest tests/unit/admin/design_review tests/unit/db/test_design_review_repository.py tests/contract/test_design_review_contracts.py tests/integration/api/test_admin_design_review_api.py --no-cov`
- `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/060-design-review-domain-foundation`
- `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml`
- `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml --start-processes`
- `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa060-after-spec`

## Review Notes

QA evidence uses the `qa060` prefix.

The QA environment uses local-principal auth and static local secret references.

The feature intentionally stores safe summaries and digests instead of raw
design prompts, completions, private messages, or raw tool payloads.
