# PR Notes: QA073 End-To-End Custom Workflow Setup Wizard And Runtime Launch

## Summary

- Added guided workflow setup checklist to the React Workflow Builder.
- Added a visible three-agent starter document transformation.
- Refreshed Workflow Builder state after successful publish.
- Added runtime launch query prefill support in the user run workspace.
- Added Design Reviews requested workflow selection support.
- Added focused frontend tests and QA073 documentation.

## Backend Contract Impact

- No new route family.
- No generated TypeScript schema change required.
- Existing save, evidence, validation, publish, runtime, and Design Review routes remain authoritative.

## Security And Redaction Review

- The checklist derives progress from safe summaries and document structure only.
- Query handoff carries safe workflow ids and tenant ids only.
- Publish readiness remains backend-owned.
- No raw prompt, completion, transcript, provider payload, credential, local path, stack trace, memory, or private channel payload is introduced.

## QA Evidence

- Focused frontend tests: workflow setup helper, WorkflowBuilderPage, UserRunPage, DesignReviewWorkspacePage.
- Full Spec QA and Playwright validation are recorded in the autopilot status after validation.
- `multi-agent-curl-test` remains required despite no curl route update.

## Reviewer Focus

- Confirm the starter is an explicit visible action and the generated workflow remains editable.
- Confirm checklist completion does not claim publish success before backend state is refreshed.
- Confirm runtime and Design Review query handoff behavior is a prefill/selection hint only.
- Confirm mobile layout keeps checklist and launch actions readable.
