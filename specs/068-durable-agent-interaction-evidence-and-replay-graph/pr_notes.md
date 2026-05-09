# PR Notes

## Summary

- Adds durable `runtime_interaction_evidence` records for ordered source/target runtime replay semantics.
- Enriches `GET /admin/runs/{workflow_run_id}/agent-graph` with replay references, interaction evidence counts, and unmapped evidence indicators.
- Reuses the operations workbench runtime graph panel so replay evidence appears alongside existing timeline, reliability, export, and log panels.
- Adds QA068 deterministic runtime seed data, Playwright flows, docs, and curl coverage for replay references and cross-tenant denial.

## Safety

- The new persistence surface stores safe summaries, node keys, statuses, classifications, artifact references, provenance digests, and idempotency keys only.
- Runtime execution records replay events idempotently for handoffs, result returns, joins, approvals, manual resolution pauses, and run completion.
- Graph text passes the existing safe graph text guardrails and does not render raw prompts, completions, secrets, provider payloads, private channel messages, memory contents, raw tool payloads, raw external payloads, or traces.

## Validation Focus

- Backend repository, interaction recording, projection, route, and graph execution tests cover mapped and unmapped replay evidence.
- React tests cover workbench loading and runtime replay graph selected details with interaction references.
- `curl_testing.md` includes strengthened section `16.5a` coverage for runtime replay evidence and section `16.8` for cross-tenant denial.
