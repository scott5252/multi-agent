# PR Notes: Generic Scenario Intake And Durable Draft Blueprint

## Summary

- Implements scenario-neutral intake, workflow key normalization, generic editable blueprint generation, durable draft creation, revision-safe saves, and tutorial label guardrails.
- Reuses existing workflow draft create action, full document save action, validation refresh, and generated React API contracts.
- Keeps authorization, tenant scope, validation, evidence, publish, launch, and redaction decisions backend-owned.
- Adds QA documents, validation manifest wiring, and autopilot status evidence.

## Reviewer Focus

- Confirm the wizard path is scenario-neutral and does not encode tutorial labels.
- Confirm the 1280 x 800 fixed-frame layout has no vertical scroll or overlap.
- Confirm saved document payloads are editable workflow documents, not hidden raw JSON templates.
- Confirm no raw secrets, prompt bodies, completions, transcripts, private payloads, local paths, stack traces, or unauthorized tenant labels appear in evidence.

## Validation Evidence

- Focused Vitest wizard tests passed.
- Frontend typecheck passed.
- Frontend build passed.
- Generated React types freshness check passed.
- Backend Console Home route assertion passed; selected single-test coverage gate is expected to fail when run alone under global coverage settings.
- Full Ruff, mypy, coverage, Spec QA, Playwright, and curl gates are tracked by the roadmap final stability gate.
