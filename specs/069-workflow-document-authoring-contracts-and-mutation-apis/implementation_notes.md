# Spec 069 Implementation Notes

## Current Behavior Audit

- The durable workflow registry already persists canonical `WorkflowDraftDocument` snapshots on every draft revision.
- The React Admin save route previously loaded the current durable document, patched only `display_name` and `description`, and saved that partial metadata update through `WorkflowRegistryService.save_draft`.
- The React builder projection exposed graph, validation, publish readiness, and summaries, but did not include the canonical document in the draft editor state.
- The generated React type file already had a `WorkflowDraftSaveRequest` interface, but it represented only metadata controls and did not appear in the schema payload hash list.

## Implemented Shape

- React builder draft state now includes the canonical `document` and backend-owned `section_summaries`.
- React save requests accept a complete document payload, change summary, and safe client context while preserving the existing metadata-only fallback.
- Full document saves validate payload size, Pydantic document shape, workflow authoring rules, revision tokens, tenant authorization, and idempotency before writing.
- Accepted React saves persist nullable revision-level idempotency fingerprints so exact duplicate submissions replay without creating duplicate revisions.
- Save mutation results may include a refreshed safe editor state and include section/field validation findings for rejected saves.

## Validation Notes

- Full document route coverage is anchored in `tests/integration/test_admin_react_routes.py`.
- Service idempotency behavior is covered in `tests/unit/admin/test_workflow_registry_service.py`.
- Schema/helper projection is covered in `tests/unit/admin/test_workflow_builder_service.py`.
- Generated contract freshness is verified with `uv run python scripts/frontend/generate_admin_react_types.py --check`.
