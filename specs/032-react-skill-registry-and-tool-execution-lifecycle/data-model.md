# Data Model: React Skill Registry And Tool Execution Lifecycle

## SkillLifecycleDashboard

Represents the authorized lifecycle page envelope.

Fields:

- `page_id`: Stable page identifier.
- `title`: Safe page title.
- `description`: Safe page summary.
- `scope`: Active `ReactAdminScope`.
- `sections`: Ordered publication, discovery, installation, credentials, readiness, eligibility, diagnostics, and audit section metadata.
- `platform_publication`: Optional `PackagePublicationWorkspace` when authorized.
- `tenant_discovery`: Optional `TenantSkillDiscovery`.
- `installations`: List of `TenantSkillInstallationSummary`.
- `connector_diagnostics`: List of `ConnectorReadinessSummary`.
- `binding_preview`: Current `BindingEligibilityPreview`.
- `audit_timeline`: List of `SkillLifecycleAuditRecord`.
- `actions`: Authorized lifecycle actions.

Safety:

- All display text is sanitized.
- Tenant labels are restricted to authorized scope.
- Browser receives safe summaries, digests, fingerprints, artifact references, status values, revision tokens, and authorized links only.

## PackagePublicationWorkspace

Represents the platform-admin package publication wizard.

Fields:

- `candidate`: `SkillPackageCandidate`.
- `available_steps`: Backend-owned wizard steps and status.
- `validation_summary`: Safe validation readiness and findings.
- `grant_preview`: Tenant grant summary for publish review.
- `publish_readiness`: Validation, smoke-test, revision, and audit readiness.
- `authorized_actions`: Manifest submit, validate, publish, quarantine, withdraw, and reload-latest actions.

Rules:

- Platform-admin only.
- Candidate state is revisioned.
- Upload content takes precedence over pasted content when both are submitted.
- Raw manifest text is not returned after submit.

## SkillPackageCandidate

Draft package candidate with safe manifest information.

Fields:

- `candidate_id`
- `package_slug`
- `candidate_revision`
- `manifest_digest`
- `manifest_source`: paste, upload, fixture, or imported.
- `safe_manifest_summary`
- `validation_status`
- `validation_findings`
- `safe_documentation_summary`
- `smoke_evidence_status`
- `publish_blockers`
- `audit_reference_id`

Rules:

- Manifest fields are rendered as summaries and finding categories.
- Raw package payloads, unsafe docs, fixture payloads, and local paths are forbidden.

## SkillPackageVersionSummary

Immutable package version summary.

Fields:

- `package_id`
- `package_slug`
- `version_id`
- `version_label`
- `lifecycle_status`: published, superseded, quarantined, withdrawn, unavailable.
- `manifest_digest`
- `safe_manifest_summary`
- `tenant_grant_summary`
- `validation_evidence_ref`
- `smoke_evidence_ref`
- `quarantine_summary`
- `withdrawal_summary`
- `audit_reference_id`
- `authorized_actions`

Rules:

- Published versions are immutable.
- Quarantine and withdrawal state is safe and auditable.
- Tenant admins only see granted versions.

## TenantSkillGrantSummary

Tenant-scoped package availability.

Fields:

- `tenant_id`
- `tenant_label`
- `package_slug`
- `version_label`
- `grant_status`
- `allowed_versions`
- `install_eligibility`
- `restrictions`
- `authorized_actions`

Rules:

- Cross-tenant grant labels are omitted.
- Platform grant mutation is platform-admin only.

## TenantSkillInstallationSummary

Tenant installation summary.

Fields:

- `installation_id`
- `tenant_id`
- `package_slug`
- `installed_version`
- `installation_revision`
- `installation_status`: ready, blocked, degraded, stale, quarantined, withdrawn, unavailable.
- `credential_readiness`
- `smoke_test_readiness`
- `connector_readiness`
- `binding_readiness`
- `upgrade_path`
- `findings`
- `authorized_actions`
- `audit_reference_id`

Rules:

- Installation state is tenant-scoped and revisioned.
- Upgrades create explicit safe mutation results.
- Stale submissions return reload-latest and retry guidance.

## CredentialReferenceOption

Safe credential reference metadata.

Fields:

- `reference_id`
- `label`
- `source_type`
- `readiness`
- `fingerprint`
- `policy_reason`
- `last_checked_label`
- `remediation`

Rules:

- Resolved values are never present.
- Options are restricted to active tenant or platform authorization.

## ConnectorReadinessSummary

First-party connector readiness summary.

Fields:

- `connector_id`
- `connector_label`: calendar, Gmail, news, weather, or commute.
- `tool_names`
- `readiness`
- `credential_status`
- `policy_status`
- `smoke_test_status`
- `staging_probe_status`
- `last_safe_summary`
- `evidence_reference_id`
- `remediation`
- `authorized_actions`

Rules:

- Local/CI uses deterministic mock or fixture evidence.
- Approved staging probe evidence is represented by references and summaries only.

## SkillExecutionDiagnosticSummary

Safe SkillExecutionGateway diagnostic.

Fields:

- `diagnostic_id`
- `skill_package_version`
- `tool_name`
- `gateway_decision`
- `side_effect_posture`
- `outbound_policy_status`
- `credential_policy_status`
- `connector_readiness`
- `safe_attempt_summary`
- `redaction_summary`
- `audit_reference_id`
- `remediation`

Rules:

- No connector request/response payloads, private messages, tool outputs, stack traces, or local paths.
- Diagnostics are scoped to authorized tenant or platform context.

## BindingEligibilityPreview

Read-only workflow/profile binding evaluation.

Fields:

- `preview_id`
- `tenant_label`
- `context_choices`
- `selected_context`
- `eligible_tools`
- `blocked_tools`
- `policy_reasons`
- `missing_requirements`
- `remediation`
- `audit_reference_id`

Rules:

- Preview does not execute tools.
- Context choices are backend-owned.
- Denied outputs use safe problem categories.

## SkillLifecycleAuditRecord

Bounded lifecycle timeline item.

Fields:

- `record_id`
- `domain`: package, candidate, grant, installation, credential, smoke_test, diagnostic, eligibility, quarantine, withdrawal.
- `package_slug`
- `version_label`
- `tenant_scope_label`
- `actor_label`
- `timestamp_label`
- `action`
- `outcome`
- `safe_diff_summary`
- `audit_reference_id`

Rules:

- Results are bounded and filterable.
- Safe diff summaries never include raw manifests, credentials, connector payloads, or unauthorized tenant labels.

## SkillLifecycleMutationResult

Shared safe lifecycle action response.

Fields:

- `status`: accepted, queued, running, confirmation_required, stale_conflict, validation_error, denied, unavailable.
- `summary`
- `toast`
- `revision`
- `warnings`
- `audit_reference_id`
- `reload_action`
- `retry_action`
- `publication`
- `installation`
- `credential`
- `smoke_test`
- `diagnostic`
- `binding_preview`

Rules:

- Mutation results include idempotency and revision evidence where applicable.
- Unsafe details are transformed into safe warnings, findings, references, or problem details.
