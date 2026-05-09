# Spec 069 PR Reviewer Notes

## Contract Review

- Review `WorkflowBuilderEnvelope.draft.document`, `section_summaries`, `WorkflowDraftSaveRequest.document`, and `BuilderMutationResult.editor_state`.
- Confirm generated React contracts are fresh and include the `idempotent_replay` mutation status.

## Redaction And Authorization

- Workflow save diagnostics return section names, field paths, digests, revision labels, and safe summaries only.
- Raw prompt bodies, completions, provider payloads, tool payloads, secrets, stack traces, and local filesystem paths must not appear in responses, logs, docs, screenshots, or curl output.
- Cross-tenant save and publish paths remain fail-closed through existing workflow registry visibility and edit checks.

## Idempotency And Stale Recovery

- React full document saves persist idempotency key, scope hash, and payload hash on accepted draft revisions.
- Exact duplicate requests replay as `idempotent_replay`; same-key/different-payload requests return validation findings without mutating the draft.
- Stale revision tokens return `stale_conflict` with safe reload guidance.

## README And Quickstart Impact

- No repository-root `README.md` or shared `docs/quickstart.md` command changes are required for Spec 069.
- Feature-specific reviewer setup lives in `quickstart.md`, `.env.qa069`, `qa069.md`, `qa069_ui.md`, and `qa069_user_guide.md`.

## Curl Coverage

- `curl_testing.md` must include deterministic create/detail/save/replay/stale/invalid coverage for `/admin/app/workflows/drafts/{workflow_draft_id}/save`.
