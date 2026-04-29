# Guided Admin Workflow Builder

The guided workflow builder extends the existing workflow registry. Platform
and tenant admins can create drafts, review metadata-driven sections, inspect a
server-derived graph preview, validate field-level findings, run a publish gate,
and trace published bundles back to source draft revisions.

## Authoring Flow

1. Open `/admin/workflows/ui`.
2. Choose `Create Workflow`.
3. Create or seed a draft with `POST /admin/workflows`.
4. Open `/admin/workflows/drafts/{workflow_draft_id}/editor`.
5. Review overview, roles, prompt/profile references, skills, contracts, graph
   nodes and edges, joins, approval gates, subworkflows, and required tests.
6. Use the advanced JSON inspector only for read-only review.

All saves use `base_revision_number`. Stale saves return `409` and create no
new revision.

## Validation Flow

Run `POST /admin/workflows/drafts/{workflow_draft_id}/validate`.

Validation records:

- canonical `field_path` and `section_key` values
- graph element ids such as `node:intake` and `edge:intake-to-review`
- prompt/profile, skill, subworkflow, and required-test readiness summaries
- graph policy findings for disconnected nodes, invalid joins, and unbounded
  cycles

## Publication Flow

Run `POST /admin/workflows/drafts/{workflow_draft_id}/publish-gate` before
publication. A ready gate includes a deterministic gate id, digest, pin summary,
reference readiness, and required test summary. `POST
/admin/workflows/drafts/{workflow_draft_id}/publish` accepts the current
validation result and optional publish gate id, then publishes through the
existing immutable workflow bundle path.

Published version details show source draft revision, publish gate digest,
prompt/profile pins, routing provenance, skill pins, subworkflow pins,
contract compatibility, graph summary, approval summary, and required-test
evidence.

## Revision And Audit Flow

Open `/admin/workflows/drafts/{workflow_draft_id}/revisions/ui` or call `GET
/admin/workflows/drafts/{workflow_draft_id}/revisions` to review immutable
revision snapshots and changed-section summaries. Restore creates a new
revision from an older snapshot and requires the current base revision.

Audit events are recorded for create, save, validation, publish gate, publish,
restore, copy, conflicts, and authorization denials with safe summaries only.
Raw prompts, provider payloads, credentials, tokens, and secret values must not
be stored in audit payloads.

## Related Files

- `src/multi_agent_platform/api/schemas/workflow_registry.py`
- `src/multi_agent_platform/api/schemas/workflow_editor.py`
- `src/multi_agent_platform/admin/workflow_registry/service.py`
- `src/multi_agent_platform/admin/workflow_registry/graph_preview.py`
- `src/multi_agent_platform/admin/workflow_registry/reference_validation.py`
- `src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- `src/multi_agent_platform/web_admin/templates/workflows/`
