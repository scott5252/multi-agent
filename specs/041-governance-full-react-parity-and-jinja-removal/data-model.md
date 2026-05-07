# Data Model: Governance Full React Parity And Jinja Removal

## Governance Dashboard Envelope

- `active_scope`: backend-authorized scope label, tenant id, and scope type.
- `sections`: ordered setup, providers, prompts, profiles, routing, history, and provenance navigation metadata.
- `summary_cards`: bounded readiness counts and safe status labels.
- `actions`: authorized platform-admin and tenant-admin action metadata.
- `legacy_routes`: governance legacy route mappings and retirement evidence.
- Validation: no section or action may be emitted unless authorized for the active principal.

## Governance Provider Detail

- `provider_id`: safe provider connection or catalog identifier.
- `display_name`: safe label.
- `mode`: OpenAI, local-compatible, or configured provider family summary.
- `health`: safe health state, latency bucket, breaker state, last probe status, and remediation hint.
- `credential`: safe credential diagnostic.
- `catalog`: tenant availability and grant readiness.
- `direct_call_guardrail`: ModelGateway-only evidence summary.
- `actions`: authorized edit, probe, credential reference, and catalog actions.
- Validation: provider mutation/probe/credential actions are platform-admin only.

## Governance Credential Diagnostic

- `reference_label`: safe secret reference label or missing state.
- `fingerprint`: non-reversible fingerprint when available.
- `resolution_status`: ready, missing, unreadable, denied, malformed, unavailable.
- `policy_reason`: safe category.
- `last_checked_at`: bounded timestamp.
- `remediation`: safe next step.
- Validation: never includes resolved values, provider tokens, authorization headers, request bodies, response bodies, or stack traces.

## Governance Prompt Detail

- `prompt_lineage_id`: safe id.
- `display_name`: safe label.
- `draft_version`: safe draft version summary.
- `published_version`: safe published version summary.
- `history`: bounded safe changes.
- `grants`: authorized tenant grants.
- `preview`: safe prompt preview state.
- `actions`: authorized save and preview action metadata.
- Validation: unsafe prompt or completion content is blocked or summarized before React receives it.

## Safe Prompt Preview Result

- `status`: rendered, summarized, blocked, denied, unavailable.
- `fixture_label`: deterministic fixture label.
- `safe_summary`: rendered summary or blocked reason.
- `findings`: redaction and policy categories.
- `audit_reference`: safe audit id.
- `artifact_reference`: optional artifact id for reviewer-safe evidence.
- Validation: no raw prompt, completion, memory, channel, connector, or tool payload.

## Governance Runtime Profile Detail

- `profile_id`: safe profile lineage or version id.
- `display_name`: safe label.
- `draft_version`: editable safe version state.
- `published_version`: immutable version state.
- `bindings`: model, provider, prompt, skill, and routing binding summaries.
- `grants`: authorized tenant grants.
- `resolution`: profile resolution preview.
- `actions`: authorized save and resolve action metadata.
- Validation: resolution is read-only and does not invoke live providers or tools.

## Governance Routing Preview

- `preview_id`: deterministic preview id.
- `input_summary`: safe input categories.
- `model_decision`: selected or denied model route summary.
- `skill_decision`: selected or denied skill route summary.
- `fallback_reason`: safe fallback category.
- `policy_reasons`: ordered policy categories.
- `direct_call_guardrail`: safe guardrail evidence.
- `audit_reference`: safe audit id.
- Validation: preview is read-only and has no external side effects.

## Governance History Record

- `record_id`: safe id.
- `domain`: provider, prompt, profile, routing, model-skill config, credential, or policy.
- `actor_summary`: redacted actor label.
- `scope`: tenant/platform scope summary.
- `change_category`: safe category.
- `outcome`: allowed, denied, blocked, degraded, unavailable.
- `safe_diff`: bounded summary.
- `audit_reference`: safe audit id.
- Validation: large diffs and raw payloads are summarized or stored as artifact references.

## Governance Run Provenance

- `run_id`: safe run id.
- `workflow_summary`: authorized workflow summary.
- `provider_summary`: provider/model route summary.
- `prompt_summary`: prompt version summary.
- `profile_summary`: runtime profile version summary.
- `credential_summary`: credential reference diagnostic summary.
- `usage_summary`: safe usage/cost summary.
- `audit_references`: bounded audit ids.
- Validation: cross-tenant provenance fails closed.

## Governance Legacy Route Mapping

- `legacy_path`: old browser path pattern.
- `react_path`: stable React destination when safe.
- `preserved_params`: safe path/query keys.
- `compatibility_status`: redirected, converted, gone, retained_with_blocker, outside_scope.
- `authorization_behavior`: authenticate first, deny safe, or unavailable safe.
- `evidence`: route tests, scanner output, docs, and reviewer notes.

## Governance Retirement Evidence Record

- `surface`: template, route, helper, static asset, docs link, or form action.
- `owner`: provider, prompt, profile, model-skill config, shared shell, or later-spec domain.
- `outcome`: deleted, redirected, converted, retained_with_blocker, outside_scope.
- `evidence_paths`: route test, scanner, docs, QA, Playwright, or PR notes.
- `rollback`: restoration scope and guardrail.
