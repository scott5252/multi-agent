# Prompt Runtime Profiles PR Notes

## Summary

Spec `012` implements prompt lineage authoring, draft validation, safe fixture
previews, immutable prompt publication, retirement, tenant grants, agent
runtime profile validation, profile activation, tenant-over-platform
resolution, model-skill prompt digest hooks, workflow validation adapters,
runtime provenance pins, shared-shell browser pages, audit classifications,
metrics, docs, and QA evidence.

## Reviewer Focus

- Immutable prompt/profile versions are never edited after publication or
  activation.
- Retired prompt and profile versions are blocked for new use but remain
  reviewable through historical pins.
- Platform prompt/profile versions require explicit tenant grants.
- Prompt previews use sanitized fixture values only and do not call models or
  live run data.
- Model-skill prompt references include prompt library version ids and digests.
- Workflow validation records profile resolution and prompt ids.
- Runtime acceptance and first-use pinning preserve prompt/profile provenance.
- Audit records, logs, metrics, and pages use safe summaries.
- Bounded prompt validation rejects oversized prompt content and fixture sets.

## Browser Acceptance

Prompt authoring should be discoverable from `/admin`, complete under seven
minutes for a prepared reviewer, and expose validation, preview, publish,
retire, grants, and history without raw database access. Profile authoring
should complete under ten minutes and expose prompt references, policy
sections, validation, activation, resolution preview, retirement, and history.

Automated browser-flow coverage passed through
`tests/integration/api/test_prompt_runtime_browser_flows.py`,
`tests/integration/api/test_agent_profile_browser_flows.py`, and
`tests/integration/api/test_prompt_runtime_admin_navigation.py` as part of the
full `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
run: 589 passed, total coverage 90.00%. The reviewer-facing QA script in
`specs/012-prompt-runtime-profiles/qa012.md` includes timed local acceptance
steps for recording the under-seven-minute prompt publish and under-ten-minute
profile activation checks during release review.

## Rollback And Retirement

Rollback is operationally handled by retiring prompt/profile versions from new
use and creating replacement versions. Historical workflow bundles and run
pins keep referencing the immutable versions they accepted.
