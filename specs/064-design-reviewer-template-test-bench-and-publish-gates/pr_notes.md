# PR Notes: Design Reviewer Template, Test Bench, And Publish Gates

## Summary

Spec 064 adds an explicit tenant Admin setup action for the reusable Design
Reviewer Council template. The setup creates or reuses a workflow draft,
attaches required Agent Test Bench evidence, evaluates current-revision publish
readiness, and exposes the result in the React Design reviews workspace.

## Reviewer Focus

- Confirm the install route is tenant-scoped and idempotent.
- Confirm required evidence covers deterministic and model backed safe modes.
- Confirm publish readiness requires the current workflow draft revision.
- Confirm template setup does not create fake design review sessions.
- Confirm Globex cannot install or inspect Acme template setup.
- Confirm Admin workspace copy stays redaction-safe and live-data only.
- Confirm `curl_testing.md` covers install, replay, workspace, and denial paths.

## Validation

- QA docs validation
- Focused template service tests
- Focused Admin API tests
- Focused React workspace tests
- Frontend typecheck and build
- Ruff, format, mypy
- Spec Kit QA
- Playwright UI validation
- Full multi-agent curl regression
