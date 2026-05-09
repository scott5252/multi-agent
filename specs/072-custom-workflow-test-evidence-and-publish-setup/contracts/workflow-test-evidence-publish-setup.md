# Contract: Workflow Test Evidence And Publish Setup

This contract describes the React-facing workflow setup evidence surface. Exact generated TypeScript names may mirror Pydantic schema names, but the behavioral contract is stable for Spec 072.

## Workflow Evidence Context

Returned with the workflow builder envelope or via a workflow-context lookup.

```json
{
  "workflow_id": "wf_opaque",
  "draft_id": "draft_opaque",
  "draft_revision": "rev_current",
  "requirements": [
    {
      "requirement_key": "required-deterministic-suite",
      "suite_id": "suite_opaque",
      "suite_label": "Safe regression suite",
      "target_type": "workflow_draft",
      "target_revision": "rev_current",
      "status": "stale",
      "freshness_summary": "Evidence must be rerun after the latest workflow edit.",
      "last_run_id": "run_opaque"
    }
  ],
  "eligible_suites": [
    {
      "suite_id": "suite_opaque",
      "suite_name": "Safe regression suite",
      "target_revision": "rev_current",
      "case_count": 2,
      "latest_run_status": "passed",
      "authorized_actions": []
    }
  ],
  "case_templates": [
    {
      "template_key": "contract-smoke",
      "label": "Contract smoke case",
      "fixture_summary": "Minimal workflow input fixture",
      "expected_contract_summary": "Valid workflow output contract",
      "assertion_summaries": ["Required output fields are present"]
    }
  ],
  "publish_gate": {
    "status": "blocked",
    "safe_reasons": ["Required test evidence is stale."],
    "remediation_links": ["#workflow-test-evidence"]
  }
}
```

Rules:

- Every string is a safe summary suitable for UI and screenshots.
- Raw transcripts, prompts, completions, provider/tool payloads, credentials, local paths, stack traces, private payloads, and unauthorized tenant labels are forbidden.
- `publish_gate.status` is derived by backend evaluation only.

## Contextual Suite Creation

Creates a Test Bench suite for the active workflow draft context.

```json
{
  "workflow_id": "wf_opaque",
  "draft_id": "draft_opaque",
  "expected_revision": "rev_current",
  "suite_name": "Safe regression suite",
  "required_for_publish": true,
  "default_safe_mode": "deterministic",
  "idempotency_key": "uuid-or-client-key"
}
```

Success response:

```json
{
  "status": "success",
  "summary": "Required suite created.",
  "suite": {
    "suite_id": "suite_opaque",
    "suite_name": "Safe regression suite",
    "target_revision": "rev_current"
  },
  "revision": "rev_after"
}
```

Failure responses:

- `409 stale_revision`: workflow draft revision no longer matches.
- `409 idempotency_conflict`: same idempotency key was used with a different payload.
- `403 denied`: tenant or principal cannot create evidence for this workflow.
- `422 unsupported_execution_mode`: requested mode is not allowed.

## Required Case Creation

Adds a deterministic case to the selected suite.

```json
{
  "suite_id": "suite_opaque",
  "template_key": "contract-smoke",
  "case_name": "Contract smoke case",
  "expected_revision": "suite_rev",
  "idempotency_key": "uuid-or-client-key"
}
```

Success response returns safe case summary and updated suite revision.

Rules:

- The server validates template eligibility, tenant scope, target type, and safe-mode constraints.
- Replays with the same idempotency key return the same result.

## Evidence Run Launch

Launches a deterministic safe run for the attached suite and active workflow draft revision.

```json
{
  "suite_id": "suite_opaque",
  "workflow_id": "wf_opaque",
  "draft_id": "draft_opaque",
  "target_revision": "rev_current",
  "safe_mode": "deterministic",
  "idempotency_key": "uuid-or-client-key"
}
```

Success response:

```json
{
  "status": "accepted",
  "summary": "Evidence run queued.",
  "run": {
    "run_id": "run_opaque",
    "suite_id": "suite_opaque",
    "target_revision": "rev_current",
    "run_status": "queued"
  },
  "refresh": {
    "mode": "poll",
    "interval_seconds": 10
  }
}
```

Rules:

- Live provider and side-effecting tool modes are rejected unless approved by backend policy.
- The run target revision must match the active workflow draft revision.

## Evidence Refresh

Refreshes the publish evidence gate for the active workflow draft.

```json
{
  "workflow_id": "wf_opaque",
  "draft_id": "draft_opaque",
  "target_revision": "rev_current"
}
```

Success response returns the `Workflow Evidence Context` shape with updated run and gate summaries.

## Workflow Requirement Attachment

The workflow full-document save contract persists `test_requirements` entries that reference eligible suites and expected revisions.

Rules:

- Requirement attachment is not valid unless the referenced suite belongs to the active tenant and matches the workflow target context.
- Saving a workflow change after evidence passes makes prior evidence stale if the target revision changes.
- Publish attempts must evaluate current workflow validation and current evidence together.
