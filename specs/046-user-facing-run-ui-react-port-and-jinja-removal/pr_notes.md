# PR Notes: Spec 046 User-Facing Run UI React Port And Jinja Removal

## Summary

- Added generated React TypeScript contracts for retained channel run lifecycle schemas.
- Added a React user run workspace for start, status, timeline, result, artifacts, prompt decisions, cancel, subscription, callback, and artifact grant actions.
- Redirected /runs and /runs/new to /admin/app/channels/runs; /runs/{run_id} continues to validate access before redirecting to React detail.
- Added scanner and route tests proving deleted run templates remain unused.
- Updated QA docs, quickstart guidance, and Spec 038 retirement notes.

## Validation Plan

- QA docs validator for specs/046-user-facing-run-ui-react-port-and-jinja-removal.
- Focused backend tests for channel run APIs, legacy redirects, cross-channel recovery, React route host, generated contracts, and Jinja retirement scanner.
- Frontend Vitest tests for UserRunPage and App run routing.
- React contract generation check and production build.
- Full run_spec_qa.py and Playwright validation using qa046.

## Redaction Notes

The React page renders safe summaries, state, trace references, artifact metadata, action status, and bounded timeline entries only. It does not render raw prompts, raw run payloads, callback secrets, local paths, stack traces, or unauthorized tenant labels.
