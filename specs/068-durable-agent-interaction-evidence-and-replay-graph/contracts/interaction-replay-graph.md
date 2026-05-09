# Contract: Interaction Replay Graph

## Existing Route

`GET /admin/runs/{workflow_run_id}/agent-graph`

Spec 068 enriches the existing runtime graph response. It does not create a separate production visualization route.

## Response Additions

### Reference Types

`AgentGraphReferenceType` adds:

- `interaction_evidence`

### Provenance Counts

`AgentGraphProvenance.evidence_counts` includes:

- `interaction_evidence`: total authorized interaction evidence rows loaded for the run
- `unmapped_interaction_evidence`: interaction evidence rows that could not be mapped to a topology edge

### Edge References

Mapped interactions appear in `AgentGraphEdge.references` as `interaction_evidence` reference summaries:

```json
{
  "reference_type": "interaction_evidence",
  "reference_id": "interaction:11111111-2222-3333-4444-555555555555",
  "label": "Replay 3: result return",
  "summary": "Coordinator returned safe result context to Specialist.",
  "status": "succeeded",
  "href": "/admin/app/operations?run_id=...&panel=timeline"
}
```

### Graph-Level Partial Evidence

Unmapped interactions are represented through graph state partial details and provenance counts. The API must not synthesize nodes or edges for unmapped production evidence.

## Authorization

The existing route authorization remains authoritative. Cross-tenant or unauthorized requests fail closed before loading interaction evidence.

## Sensitive Data Contract

The response must not include raw prompts, completions, provider responses, credentials, authorization headers, private channel payloads, memory contents, stack traces, raw tool outputs, or redacted metadata payload values.

## Curl Coverage

`curl_testing.md` must continue to cover the runtime graph success and cross-tenant denial route family. Spec 068 strengthens the success assertion to include interaction replay evidence counts and at least one `interaction_evidence` reference.
