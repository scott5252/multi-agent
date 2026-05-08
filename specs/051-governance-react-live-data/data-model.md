# Data Model: Governance React Live Data

## React Governance Envelope

- **Purpose**: Top-level page payload for `/admin/app/governance/bootstrap.json`.
- **Fields**: page identity, active scope, sections, setup/empty-state summaries, provider summaries, prompt summaries, profile summaries, routing preview state, profile resolution state, prompt preview state, policy history, run provenance, legacy route mappings, actions, provenance metadata.
- **Relationships**: Aggregates the live summaries below for the active platform or tenant scope.
- **Validation Rules**: All user-facing strings pass governance safe-text validation; empty collections include empty-state metadata; denied/unavailable states never include unauthorized labels.

## Provider Governance Summary

- **Purpose**: Redaction-safe view of an authorized model provider connection and its readiness.
- **Fields**: provider id/key, display name, provider type, active/status, tenant availability, model count, latest health state, latest test outcome, credential-reference readiness, local no-auth status, direct-call guardrail, available actions.
- **Source**: Provider connection/model/tenant visibility records, latest provider test/health records, gateway/probe diagnostics, secret-reference readiness metadata.
- **State Transitions**: untested -> ready/degraded/blocked/unavailable; active -> inactive; visible -> revoked.
- **Validation Rules**: Never include credential values, provider authorization headers, raw request/response payloads, or unsafe local paths.

## Prompt Governance Summary

- **Purpose**: Safe view of prompt lineages, drafts, versions, grants, and render-test readiness.
- **Fields**: lineage id, display name, status, draft revision, published version, tenant grants, validation/render-test status, safe change summary, history, authorized actions.
- **Source**: Prompt lineage, draft, draft revision, version, validation result, and tenant grant records.
- **State Transitions**: draft active -> revised -> validated -> published -> granted/retired.
- **Validation Rules**: Raw prompt template content and raw render-test transcript content are not rendered; previews expose safe output summaries only.

## Runtime Profile Governance Summary

- **Purpose**: Safe view of runtime profile drafts, versions, validation, activation, grants, and resolution.
- **Fields**: profile id/key, display name, agent kind, status, draft revision, active version, validation state, prompt references, model routing hints, skill/tool expectations, grants, history, authorized actions.
- **Source**: Agent runtime profile, draft revision, validation, version, active pointer, and tenant grant records.
- **State Transitions**: draft active -> revised -> validated -> activated -> granted/retired.
- **Validation Rules**: Profile summaries expose references and safe metadata, not raw prompt content or hidden tool payloads.

## Routing And Policy Summary

- **Purpose**: Safe view of model routing versions, routing previews, policy records, rollbacks, and config history.
- **Fields**: route/config id, version id, status, effective scope, selected provider/model summary, tool/outbound/credential policy summary, policy history event, audit reference.
- **Source**: Model-skill configuration repository, active config pointers, policy records, preview service results, audit history.
- **State Transitions**: draft/configured -> activated -> retired/rolled back; preview unavailable -> available/degraded.
- **Validation Rules**: Preview output is read-only and must not execute providers or connectors.

## Gateway Diagnostic And Run Provenance Summary

- **Purpose**: Redaction-safe operational evidence linking provider attempts and runtime runs to governance configuration.
- **Fields**: run id or operation id, provider connection id, prompt/profile/config version references, attempt status, health state, safe failure category, redaction notice, audit/reference links.
- **Source**: Gateway operation/attempt records, health snapshots, usage/provenance records, run timeline/bundle metadata, audit events.
- **State Transitions**: unavailable -> available/summarized/degraded/denied; attempt running -> success/failure.
- **Validation Rules**: Raw prompts, completions, request/response bodies, memory contents, channel messages, stack traces, and filesystem paths are prohibited.

## Empty, Denied, And Unavailable State

- **Purpose**: Honest replacement for deterministic governance rows when live records do not exist or cannot be shown.
- **Fields**: state id, title, summary, remediation, source kind, source detail, optional action.
- **Source**: Projection service decisions after repository reads and authorization checks.
- **Validation Rules**: Must not invent row identifiers or pass/fail evidence.
