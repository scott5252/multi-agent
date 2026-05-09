# PR Notes: Spec 062 - Design Review Coordinator And Iteration Loop

## Summary

Spec 062 adds a design review coordinator service and JSON API routes.

The coordinator launches one acyclic DB-backed runtime run per review round.

The coordinator records assignments, safe verdicts, quorum decisions, revisions,
manual decisions, and handoffs using existing design review tables.

Quorum supports four-of-five and three-of-four policies with zero blockers.

Revision loops create immutable next revisions.

Manual decisions support revise, approve by exception, retry, and cancel.

## Validation

```bash
uv run pytest tests/unit/admin/design_review/test_design_review_coordinator.py tests/contract/test_design_review_coordinator_contracts.py tests/integration/api/test_admin_design_review_coordinator_api.py tests/integration/runtime/test_design_review_coordinator_runtime.py --no-cov
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/062-design-review-coordinator-and-iteration-loop
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa062-after-spec
```

## Curl Testing Note

`curl_testing.md` now includes QA062 coordinator coverage for state, launch,
completion, manual decisions, and cross-tenant denial.
