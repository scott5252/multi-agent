# PR Notes: Spec 072 - Custom Workflow Test Evidence And Publish Setup

## Summary
Spec 072 adds a React workflow evidence setup panel that lets tenant admins attach required Test Bench suites, add safe deterministic cases, launch safe evidence runs, and inspect backend-owned publish readiness from the workflow builder.

The implementation reuses existing Test Bench APIs and publish gate behavior. No new public route family was added.

## Implementation Notes
- Added workflow `test_requirements` editor normalization and graph accessibility summaries.
- Added workflow evidence helpers for readiness summaries, requirement creation, run updates, artifact label safety, and redaction.
- Added `WorkflowTestEvidencePanel` to the workflow builder.
- Linked publish and validation evidence blockers back to `#workflow-test-evidence`.
- Added focused frontend coverage for helper behavior, panel launch flow, publish links, and validation links.
- Added QA072 deterministic seed data with a current passing suite/run plus stale and failed suites for negative review.
- Added QA072 guide, UI walkthrough, manual user guide, environment file, and validation manifest updates.

## Safety And Tenancy
- Current evidence is evaluated by backend services against the exact workflow draft revision.
- Browser state does not synthesize passing evidence or override publish blockers.
- Workflow summaries use safe text and opaque IDs.
- Cross-tenant access remains denied by existing workflow and Test Bench authorization checks.
- Live provider, Telegram, and external connector paths remain disabled in QA072.

## Curl Coverage Decision
No `curl_testing.md` update was required for Spec 072 because the implementation reuses existing route families:

- `/admin/agent-tests/*` JSON API coverage is already present in section 10.
- `/admin/app/test-bench/*` React workspace API coverage is already present in section 18.
- `/admin/app/workflows/*` React workflow builder, save, validation, and publish coverage is already present in section 18.

The required post-spec curl regression is still run with output under `.data/curl_test_runs/qa072-after-spec`.

## Validation Plan
- Focused backend workflow registry, workflow builder, admin React contract, and admin React route tests.
- Focused frontend workflow evidence tests and TypeScript typecheck.
- Generated React type freshness.
- Ruff check, Ruff format check, and mypy.
- Frontend production build.
- QA docs validation.
- Spec QA manifest.
- Playwright desktop and mobile workflow evidence screenshots.
- Multi-agent curl regression.

## Reviewer Notes
Reviewers should start with the evidence panel in the QA072 workflow builder, then open the Test Bench workspace to confirm the current suite and run are persisted records. Publish readiness should be treated as backend-owned. Any protected material in UI, API output, screenshots, or notes is a release blocker.
