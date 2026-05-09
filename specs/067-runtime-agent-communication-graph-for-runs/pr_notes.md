# PR Notes

## Summary

- Adds `GET /admin/runs/{workflow_run_id}/agent-graph` for tenant-scoped runtime communication graph projections.
- Reuses the design-time `AgentGraphPanel` inside the operations workbench so timeline, reliability, export, and log panels remain available.
- Extends generated React contracts with runtime graph provenance, runtime reference types, edge statuses, and edge references.
- Adds QA067 deterministic runtime seed data, Playwright flows, docs, and curl coverage for success and cross-tenant denial.

## Safety

- No new runtime persistence tables are introduced.
- Runtime graph evidence is inferred from existing run steps, runtime timeline events, handoffs, side effects, approvals, bundle metadata, and published topology.
- Graph text passes the existing safe graph text guardrails and does not render raw prompts, completions, secrets, provider payloads, private channel messages, memory contents, raw tool payloads, or traces.

## Validation Focus

- Backend projection and route tests cover completed, retrying, paused, partial, missing, and denied states.
- React tests cover workbench loading and runtime graph selected details.
- `curl_testing.md` includes section `16.5a` for runtime graph success and section `16.8` for cross-tenant denial.
