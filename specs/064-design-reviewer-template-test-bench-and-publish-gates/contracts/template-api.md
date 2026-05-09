# Contract: Design Reviewer Council Template API

## POST `/admin/design-reviews/templates/council/install`

Installs or reuses the reusable Design Reviewer Council workflow template for
the active tenant.

### Request

```json
{
  "tenant_id": "00000000-0000-0000-0000-000000000000",
  "template_key": "design-reviewer-council",
  "idempotency_key": "qa064-install-acme",
  "run_required_tests": true,
  "safe_mode": "deterministic"
}
```

### Success Response

```json
{
  "template_key": "design-reviewer-council",
  "tenant_id": "00000000-0000-0000-0000-000000000000",
  "workflow_draft_id": 101,
  "workflow_lineage_id": 55,
  "workflow_draft_revision_id": 202,
  "workflow_key": "design-reviewer-council",
  "display_name": "Design Reviewer Council",
  "agent_test_suite_id": 303,
  "agent_test_run_id": 404,
  "required_evidence_status": "passing",
  "publish_gate_status": "ready",
  "replayed": false,
  "safe_summary": "Council template installed with current safe evidence.",
  "actions": [
    {
      "label": "Open workflow draft",
      "href": "/admin/app/workflows/drafts/101"
    }
  ]
}
```

### Error Responses

- `403`: Principal is not authorized for the target tenant or route surface.
- `404`: Tenant or required draft dependency is not visible to the principal.
- `409`: Existing template setup is stale, conflicted, or cannot be safely
  reused.
- `422`: Request is invalid or includes unsafe visible text.

## GET `/admin/app/design-reviews/bootstrap.json`

Existing Spec 063 workspace envelope is extended with a `template_setup` field.

### Added Envelope Field

```json
{
  "template_setup": {
    "status": "ready",
    "template_key": "design-reviewer-council",
    "workflow_draft_id": 101,
    "workflow_draft_revision_id": 202,
    "agent_test_suite_id": 303,
    "latest_run_id": 404,
    "publish_gate_status": "ready",
    "safe_summary": "Council template has current required evidence.",
    "primary_action": {
      "kind": "install_template",
      "label": "Install council template",
      "method": "POST",
      "href": "/admin/design-reviews/templates/council/install"
    }
  }
}
```

When no template is installed, `status` is `not_installed` and identifiers are
omitted. The envelope must not fabricate sessions, reviewer rows, quorum
decisions, or handoffs.
