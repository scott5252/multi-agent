# Contract: Workflow Document Authoring Contracts And Mutation APIs

## Existing Route Family

Spec 069 extends the existing React Admin workflow builder route family:

- `GET /admin/app/workflows/builder.json`
- `GET /admin/app/workflows/drafts/{workflow_draft_id}/detail.json`
- `POST /admin/app/workflows/drafts/{workflow_draft_id}/save`

The lower-level workflow registry routes under `/admin/workflows/...` remain supported.

## Editor Load Response

`WorkflowBuilderEnvelope.draft` is expanded from the current summary-only projection to a safe editor state that includes:

- `workflow_draft_id`
- `workflow_lineage_id`
- `revision`
- `name`
- `description`
- `status`
- `tenant_label`
- `document`
- `section_summaries`
- `graph`
- `validation`
- `publish_readiness`

The `document` value is the canonical `WorkflowDraftDocument` shape from the workflow registry contract.

## Save Request

`POST /admin/app/workflows/drafts/{workflow_draft_id}/save`

```json
{
  "revision": "1",
  "idempotency_key": "workflow-save-11111111-2222-4333-8444-555555555555",
  "document": {
    "workflow_key": "custom-review-flow",
    "display_name": "Custom Review Flow",
    "description": "Tenant authored workflow.",
    "workflow_kind": "main_workflow",
    "entry_node_key": "start",
    "roles": [],
    "prompt_profile_references": [],
    "skill_installations": [],
    "contracts": [],
    "nodes": [
      {
        "node_key": "start",
        "node_type": "terminal",
        "display_name": "Start"
      }
    ],
    "edges": [],
    "join_policies": [],
    "approval_gates": [],
    "subworkflow_refs": [],
    "test_requirements": [],
    "editor_annotations": {
      "section_notes": {},
      "graph_layout": {},
      "collapsed_sections": []
    }
  },
  "change_summary": "Saved custom workflow document"
}
```

## Accepted Response

```json
{
  "status": "accepted",
  "summary": "Draft saved as a durable workflow revision.",
  "revision": "2",
  "audit_reference_id": "workflow-draft:...:revision:2",
  "validation": {
    "status": "unavailable",
    "revision": "2",
    "summary": "No durable validation result exists for the current draft revision."
  },
  "stale_conflict": null
}
```

The response may include an updated editor state when the implementation keeps the envelope in the mutation result. Any included editor state must be redaction-safe and generated from durable state after persistence.

## Idempotent Replay Response

Exact same tenant, principal, draft, route family, revision intent, idempotency key, and payload hash returns the same current safe revision result without creating a duplicate revision.

```json
{
  "status": "idempotent_replay",
  "summary": "Workflow draft save was already applied for this idempotency key.",
  "revision": "2",
  "idempotency": {
    "replayed": true,
    "scope": "workflow-document-save"
  }
}
```

## Idempotency Conflict Response

Same idempotency key with a different payload or target returns a safe validation/problem result. It must not mutate the draft.

## Stale Conflict Response

```json
{
  "status": "stale_conflict",
  "summary": "Reload the current draft revision before saving again.",
  "stale_conflict": {
    "submitted_revision": "1",
    "current_revision": "2",
    "message": "Reload the current draft revision before saving again.",
    "reload_href": "/admin/app/workflows/drafts/{workflow_draft_id}"
  }
}
```

## Validation Failure Response

Invalid documents return safe findings mapped to sections and field paths:

```json
{
  "status": "validation_error",
  "summary": "Workflow document has blocking validation findings.",
  "validation": {
    "status": "blocked",
    "findings": [
      {
        "finding_id": "graph.blocking",
        "severity": "blocking",
        "category": "graph",
        "section": "graph",
        "message": "Edges must reference existing nodes.",
        "recommended_action": "Update the referenced builder field and rerun validation.",
        "href": "#workflow-graph"
      }
    ]
  }
}
```

## Authorization And Redaction

- Unauthorized or cross-tenant requests fail closed before loading draft document payloads.
- Tenant admins cannot save platform-scoped drafts unless explicitly authorized.
- Responses, audit summaries, logs, screenshots, docs, and curl artifacts must not expose raw secrets, credential values, provider authorization headers, raw prompt bodies outside authorized prompt edit forms, completions, memory contents, private channel messages, raw tool payloads, raw test transcripts, local filesystem paths, stack traces, or unauthorized tenant labels.

## Curl Coverage

`curl_testing.md` must include sequential setup and success/error checks for the React workflow document save route family:

- Create or load a deterministic workflow draft.
- Save a complete document with roles, contracts, nodes, edges, joins, prompt/profile references, test requirements, and annotations.
- Reload and verify the saved sections are present.
- Submit a stale revision and verify stale conflict.
- Submit an invalid graph reference and verify section/field validation findings.
