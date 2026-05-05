# Data Model: Model, Prompt, Profile, And Provider Governance

## GovernanceDashboard

Represents the authorized governance page envelope.

Fields:

- `page_id`: Stable page identifier.
- `title`: Safe page title.
- `description`: Safe page summary.
- `scope`: Active `ReactAdminScope`.
- `shell`: Optional `ReactAdminShellState`.
- `sections`: Ordered Setup, Prompts, Profiles, Routing, Providers, and Provenance section metadata.
- `setup_summary`: Overall readiness, blockers, warnings, and recommended next actions.
- `providers`: List of `ProviderGovernanceSummary`.
- `prompts`: List of `PromptLibrarySummary`.
- `profiles`: List of `RuntimeProfileGovernanceSummary`.
- `routing_preview`: Current `RoutingPreviewResult`.
- `policy_history`: List of `PolicyHistoryRecord`.
- `run_provenance`: List of `RunProvenanceSummary`.
- `actions`: Authorized probe, preview, resolve, routing, history, and mutation actions.

Safety:

- All display text is sanitized.
- Tenant labels are restricted to authorized scope.
- Browser receives only safe summaries, statuses, fingerprints, artifact references, and links.

## ProviderGovernanceSummary

Safe provider catalog and health representation.

Fields:

- `provider_id`
- `provider_key`
- `display_name`
- `provider_type`: OpenAI, local OpenAI-compatible, or other catalog type.
- `status`: ready, degraded, unavailable, disabled, denied.
- `tenant_availability`: Platform, tenant-granted, unavailable, or denied.
- `model_count`
- `health`: Last-known health summary, latency bucket, breaker state, and checked-at label.
- `credential_reference`: `ProviderCredentialReference`.
- `local_no_auth`: Allowlist status and reason.
- `direct_call_guardrail`: Safe ModelGateway/direct-SDK guardrail summary.
- `probe_action`: Authorized action metadata when platform admin.
- `links`: Authorized details, operations, usage, and audit links.

Safety:

- No provider tokens, authorization headers, request bodies, response bodies, raw attempts, or resolved credential values.
- Unauthorized providers do not reveal tenant labels or sensitive provider names.

## ProviderCredentialReference

Safe credential reference metadata.

Fields:

- `reference_id`
- `label`
- `source_type`: Secret provider, environment reference, local fake secret, or none.
- `fingerprint`
- `readiness`: ready, missing, invalid, unauthorized, unavailable, not_required.
- `last_resolution_status`
- `last_checked_label`
- `policy_reason`
- `remediation`

Rules:

- Reference IDs and fingerprints are safe identifiers only.
- Resolved values are never present.
- Missing or invalid references produce safe diagnostics.

## ProviderProbeDiagnostic

Explicit provider probe result.

Fields:

- `probe_id`
- `provider_id`
- `status`: passed, degraded, failed, denied, unavailable.
- `summary`
- `latency_bucket`
- `failure_category`
- `retry_state`
- `breaker_state`
- `credential_resolution_status`
- `audit_reference_id`
- `redaction_summary`

Rules:

- Probes are explicit actions.
- Local/CI probes use deterministic mocked adapters.
- Raw provider payloads and raw credential data are forbidden.

## PromptLibrarySummary

Safe prompt lineage/version representation.

Fields:

- `prompt_lineage_id`
- `name`
- `status`: draft, published, archived, blocked.
- `draft_version`
- `published_version`
- `tenant_grants`
- `render_test_status`
- `safe_change_summary`
- `history`
- `draft_action`
- `publish_action`
- `preview_action`
- `links`

Safety:

- Raw prompt body is not included by default.
- Version history uses safe change categories and audit references.
- Draft and publish actions return safe mutation results and revision tokens.

## SafePromptPreview

Fixture-backed render preview result.

Fields:

- `preview_id`
- `prompt_lineage_id`
- `fixture_label`
- `status`: rendered, summarized, blocked, unavailable.
- `safe_output`
- `redaction_findings`
- `variable_summary`
- `artifact_reference_id`
- `audit_reference_id`

Rules:

- Unsafe raw prompts and completions are blocked or summarized before React.
- Preview does not call live providers in local/CI validation.

## RuntimeProfileGovernanceSummary

Safe runtime profile configuration representation.

Fields:

- `profile_id`
- `profile_lineage_id`
- `name`
- `status`
- `draft_version`
- `published_version`
- `model_binding`
- `provider_binding`
- `prompt_binding`
- `skill_requirements`
- `tenant_grants`
- `resolver_status`
- `authorized_actions`
- `save_action`
- `links`

Safety:

- Model/provider/prompt/skill bindings are safe summaries.
- Unauthorized grants are omitted.
- Safe profile field changes return revisioned mutation results.

## ProfileResolutionPreview

Read-only profile resolver output.

Fields:

- `preview_id`
- `profile_id`
- `status`: resolved, fallback, denied, unavailable.
- `selected_profile_version`
- `model_route`
- `provider_route`
- `prompt_route`
- `skill_route`
- `fallback_reason`
- `policy_reasons`
- `remediation`
- `audit_reference_id`

Rules:

- No provider execution occurs.
- Denied outputs use safe problem categories.

## RoutingPreviewResult

Read-only model/skill routing policy evaluation.

Fields:

- `preview_id`
- `tenant_id`
- `workflow_context_label`
- `status`: allowed, fallback, denied, unavailable.
- `model_decision`
- `provider_decision`
- `skill_decision`
- `policy_reasons`
- `direct_call_guardrail`
- `credential_reference_status`
- `audit_reference_id`
- `remediation`

Rules:

- Preview never calls live model providers, credential stores, Telegram, external tools, or direct SDKs in local/CI.
- Output is safe for screenshots and docs.

## PolicyHistoryRecord

Safe policy/configuration history item.

Fields:

- `history_id`
- `domain`: provider, prompt, profile, routing, credential, guardrail, provenance.
- `actor_label`
- `tenant_scope_label`
- `timestamp_label`
- `change_category`
- `outcome`
- `safe_diff_summary`
- `audit_reference_id`
- `links`

Rules:

- Results are bounded and filterable.
- Diffs are category summaries, not raw documents.

## RunProvenanceSummary

Safe run-level provenance evidence.

Fields:

- `run_id`
- `tenant_label`
- `workflow_label`
- `started_at_label`
- `provider_evidence`
- `model_evidence`
- `prompt_evidence`
- `profile_evidence`
- `routing_evidence`
- `credential_reference_evidence`
- `usage_evidence`
- `audit_reference_id`
- `links`

Safety:

- No raw prompts, completions, memory, provider payloads, connector payloads, private channel text, or unauthorized tenant labels.

## GovernanceMutationResult

Shared result for provider, credential, prompt, profile, probe, preview, resolve, and routing actions.

Fields:

- `status`: accepted, denied, validation_error, stale_conflict, dependency_unavailable, degraded, blocked, replayed.
- `summary`
- `toast`
- `revision`
- `warnings`
- `field_errors`
- `diagnostics`
- `audit_reference_id`
- `redirect_href`

Rules:

- Mutation results are safe to render and store in QA artifacts.
- Platform-only actions must deny tenant principals without leaking target details.
