# Contract: Workflow Publish Required Test Evidence

## Workflow Validation Response

Endpoint:

```text
POST /admin/workflows/drafts/{workflow_draft_id}/validate
```

Relevant response fields:

```json
{
  "status": "failed",
  "blocking_issue_count": 1,
  "findings": [
    {
      "category": "required_test",
      "severity": "blocking",
      "code": "reference.required_test.not_passing",
      "field_path": "test_requirements[0].suite_id",
      "section_key": "tests",
      "reference_type": "test_suite",
      "reference_id": "daily-briefing-smoke",
      "message": "Required workflow test evidence is missing, stale, or failing.",
      "remediation": "Run the required suite against the current draft revision and rerun validation.",
      "blocking": true
    }
  ],
  "reference_readiness": [
    {
      "reference_type": "test_suite",
      "reference_key": "daily-briefing-smoke",
      "status": "missing",
      "blocking": true,
      "safe_summary": "Required test evidence is unavailable for the current workflow revision.",
      "pin_payload": {
        "requirement_key": "daily-briefing-smoke",
        "suite_id": "00000000-0000-0000-0000-000000000000",
        "target_type": "workflow_draft",
        "target_id": "11111111-1111-1111-1111-111111111111",
        "target_version": "22222222-2222-2222-2222-222222222222",
        "status": "missing",
        "freshness_policy": "latest_revision"
      }
    }
  ],
  "required_test_summary": {
    "required_count": 1,
    "passing_count": 0,
    "failing_count": 0,
    "missing_count": 1,
    "stale_count": 0
  },
  "publish_blocking": true
}
```

## Publish Gate Response

Endpoint:

```text
POST /admin/workflows/drafts/{workflow_draft_id}/publish-gate
```

Relevant response fields:

```json
{
  "status": "blocked",
  "blocking_issue_count": 1,
  "reference_readiness": [
    {
      "reference_type": "test_suite",
      "reference_key": "daily-briefing-smoke",
      "status": "stale",
      "blocking": true,
      "safe_summary": "A passing run exists, but not for the current workflow revision.",
      "pin_payload": {
        "requirement_key": "daily-briefing-smoke",
        "suite_id": "00000000-0000-0000-0000-000000000000",
        "passing_run_id": "33333333-3333-3333-3333-333333333333",
        "target_type": "workflow_draft",
        "target_id": "11111111-1111-1111-1111-111111111111",
        "target_version": "22222222-2222-2222-2222-222222222222",
        "evidence_target_version": "old-revision",
        "status": "stale"
      }
    }
  ],
  "required_test_summary": {
    "required_count": 1,
    "passing_count": 0,
    "failing_count": 0,
    "missing_count": 0,
    "stale_count": 1
  },
  "pin_summary": {
    "required_test_evidence": [
      {
        "requirement_key": "daily-briefing-smoke",
        "suite_id": "00000000-0000-0000-0000-000000000000",
        "status": "stale"
      }
    ]
  }
}
```

## Final Publication

Endpoint:

```text
POST /admin/workflows/drafts/{workflow_draft_id}/publish
```

Publication must:

- Resolve the requested validation result.
- Confirm it is current for the draft revision.
- Re-query required test evidence for the current revision.
- Reject mismatched `publish_gate_id`.
- Reject any gate status other than `ready`.
- Persist safe required-test evidence in version `summary_json`.

## Safety Requirements

- Responses must not expose raw fixture JSON, expected contract payloads, redacted transcript bodies, prompt text, secret values, credential references beyond existing safe IDs, tenant names for denied records, or object-storage payload contents.
- Cross-tenant suite IDs are treated as unavailable; diagnostics must not confirm the foreign tenant or suite name.
