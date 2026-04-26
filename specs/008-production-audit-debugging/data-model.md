# Data Model: Production Audit And Debugging

## AuditTimelineEvent

Append-only lifecycle or runtime event for one workflow run.

**Fields**: `timeline_event_id`, `tenant_id`, `workflow_run_id`,
`parent_run_id`, `run_step_id`, `sequence`, `event_category`,
`run_status_after`, `origin_type`, `origin_ref`, `actor_principal_id`,
`trace_id`, `correlation_id`, `source_event_id`, `occurred_at`,
`recorded_at`, `criticality`, `safe_summary`, `safe_details`,
`classification_version`, `supersedes_event_id`.

**Relationships**: Owns many RuntimeTraceRecords and CaptureGapMarkers. May
reference one RunLineageLink, VersionBundleSnapshot, NotificationDeliveryView,
or SecretAccessAuditRecord through trace records.

**Validation rules**: `(tenant_id, workflow_run_id, sequence)` is unique and
monotonic. `(tenant_id, workflow_run_id, event_category, source_event_id)` is
idempotent. `safe_details` must pass classification before persistence.

**State transitions**: Rows are immutable. Corrections, redactions, and
supersession are represented by later timeline events.

## RuntimeTraceRecord

Operator-visible evidence linked to a timeline event.

**Fields**: `trace_record_id`, `tenant_id`, `workflow_run_id`,
`timeline_event_id`, `run_step_id`, `trace_type`, `trace_id`,
`correlation_id`, `status`, `outcome`, `duration_ms`, `policy_outcome`,
`subject_ref`, `safe_input_summary`, `safe_output_summary`,
`safe_error_summary`, `metadata`, `occurred_at`, `recorded_at`.

**Relationships**: Specialized records for handoffs, validations, memory
writes, tool usage, model selection, notifications, and secret access use this
row as the common query surface.

**Validation rules**: Must link to an AuditTimelineEvent in the same tenant
and run. Safe summaries are bounded and may contain identifiers, categories,
digests, counts, and redacted field names only.

## AgentHandoffTrace

Specialized trace data for agent-to-agent handoff decisions.

**Fields**: `trace_record_id`, `source_agent_key`, `destination_agent_key`,
`handoff_reason`, `handoff_outcome`, `handoff_contract_ref`,
`payload_schema_ref`, `payload_digest`, `safe_payload_metadata`.

**Relationships**: Extends RuntimeTraceRecord with `trace_type = agent_handoff`.

**Validation rules**: Raw handoff payloads are not stored. Contract references
must be safe identifiers or version references.

## ContractValidationTrace

Evidence for contract validation pass/fail outcomes.

**Fields**: `trace_record_id`, `contract_name`, `contract_version`,
`validation_target`, `validation_outcome`, `error_count`,
`safe_error_summary`, `prioritized_error_codes`.

**Relationships**: Extends RuntimeTraceRecord with
`trace_type = contract_validation`.

**Validation rules**: Validation details must not expose unauthorized payload
content. Multiple errors are summarized with stable error codes and counts.

## MemoryWriteAuditTrace

Evidence for memory write attempts and outcomes.

**Fields**: `trace_record_id`, `memory_scope_id`, `write_intent`,
`requested_version_ref`, `effective_version_ref`, `projection_ref`,
`write_outcome`, `superseded_by_ref`, `safe_memory_summary`.

**Relationships**: Extends RuntimeTraceRecord with
`trace_type = memory_write` and links to immutable memory versions where
authorized.

**Validation rules**: Memory content is never stored in audit trace summaries.
Rejected, accepted, superseded, archived, and unavailable states are distinct.

## ToolUsageTrace

Evidence for external or internal tool use.

**Fields**: `trace_record_id`, `tool_id`, `tool_name`, `action_category`,
`policy_decision_id`, `policy_outcome`, `execution_outcome`, `duration_ms`,
`destination_category`, `safe_input_summary`, `safe_output_summary`,
`safe_failure_reason`.

**Relationships**: Extends RuntimeTraceRecord with `trace_type = tool_usage`.
May link to SecretAccessAuditRecord when credentials were requested.

**Validation rules**: Tool arguments and outputs are summarized or redacted.
Denied tool decisions must not have external side-effect evidence.

## ModelSelectionTrace

Evidence for model and prompt resolution.

**Fields**: `trace_record_id`, `model_provider_key`, `model_id`,
`selection_source`, `model_routing_version_id`, `prompt_reference_version_id`,
`workflow_bundle_ref`, `agent_key`, `step_key`, `selection_outcome`,
`safe_trace_metadata`.

**Relationships**: Extends RuntimeTraceRecord with
`trace_type = model_selection` and links to VersionBundleSnapshot.

**Validation rules**: Prompt bodies, raw provider messages, provider tokens,
and unauthorized model payload content are not stored or rendered.

## VersionBundleSnapshot

Pinned execution context visible during run inspection.

**Fields**: `version_bundle_snapshot_id`, `tenant_id`, `workflow_run_id`,
`workflow_lineage_id`, `workflow_version_bundle_id`, `execution_bundle_id`,
`bundle_digest`, `workflow_version`, `contract_version_refs`,
`prompt_version_refs`, `model_config_version_refs`, `tool_policy_version_refs`,
`activation_state_at_acceptance`, `accepted_at`, `migration_record_refs`,
`safe_summary`.

**Relationships**: One snapshot belongs to a workflow run and is referenced by
timeline, replay, lineage, and export responses.

**Validation rules**: Snapshot is created before agent work starts. Resume uses
the original snapshot unless an audited migration record exists.

## RunLineageLink

Graph edge between related workflow runs.

**Fields**: `run_lineage_link_id`, `tenant_id`, `source_run_id`,
`target_run_id`, `relationship_type`, `source_timeline_event_id`,
`source_trace_record_id`, `created_at`, `status`, `safe_reason`.

**Relationships**: Connects parent runs, child runs, retries, resumptions, and
delegated executions. Timeline and replay views use lineage links for graph
navigation.

**Validation rules**: Source and target must share tenant scope unless a future
approved cross-tenant delegation model exists. Unauthorized viewers receive
redacted boundary nodes instead of hidden raw ids.

## NotificationDeliveryTrace

Run-debug view over notification attempts.

**Fields**: `trace_record_id`, `notification_delivery_attempt_id`,
`destination_category`, `delivery_status`, `attempt_count`,
`latest_attempt_at`, `safe_failure_reason`, `triggering_timeline_event_id`,
`provider_correlation_ref`.

**Relationships**: Extends RuntimeTraceRecord with
`trace_type = notification_delivery` and references existing channel delivery
attempt records.

**Validation rules**: Destination values are category-level or masked. Delivery
states distinguish scheduled, delivered, retrying, failed, suppressed, and
unavailable.

## SecretAccessAuditRecord

Governance audit metadata for secret or credential reference requests.

**Fields**: `secret_access_audit_record_id`, `tenant_id`, `workflow_run_id`,
`timeline_event_id`, `trace_record_id`, `requester_type`, `requester_ref`,
`secret_reference_id`, `secret_reference_version`, `credential_scope`,
`policy_outcome`, `access_outcome`, `reason_code`, `safe_reason`,
`requested_at`, `recorded_at`, `trace_id`.

**Relationships**: May link to ToolUsageTrace, ModelSelectionTrace, or a
policy-denial timeline event.

**Validation rules**: Raw secret values, delegated credential values, provider
tokens, and decrypted metadata are forbidden. Capture failures fail closed.

## CaptureGapMarker

Explicit marker for missing non-security trace data.

**Fields**: `capture_gap_id`, `tenant_id`, `workflow_run_id`,
`timeline_event_id`, `trace_id`, `gap_type`, `affected_trace_type`,
`criticality`, `safe_reason`, `detected_at`, `recorded_at`,
`recovery_status`.

**Relationships**: Belongs to a timeline event and is rendered in timeline and
replay responses.

**Validation rules**: Only `diagnostic` or approved non-blocking
`runtime_required` gaps may continue execution. `security_governance` gaps
must fail closed instead.

**State transitions**: `open` -> `resolved`; `open` -> `superseded`;
terminal states are append-only events.

## InspectionAccessAuditEvent

Audit event for admin inspection, search, export, or denied access.

**Fields**: `inspection_access_audit_event_id`, `tenant_id`,
`actor_principal_id`, `actor_role`, `action`, `target_run_id`,
`target_trace_record_id`, `authorization_outcome`, `denial_category`,
`filters_digest`, `export_id`, `trace_id`, `safe_metadata`, `created_at`.

**Relationships**: Links to DebugEvidenceExport when action is export/create
or export/share.

**Validation rules**: Denied attempts are recorded with fail-closed behavior
before returning the response when possible. Filter values are digested or
bounded to avoid storing sensitive search text.

## DebugEvidenceExport

Redacted artifact package for support, review, or incident response.

**Fields**: `debug_evidence_export_id`, `tenant_id`, `requested_by`,
`workflow_run_id`, `lineage_scope`, `recipient_scope`, `redaction_profile`,
`status`, `artifact_id`, `artifact_ref`, `included_sections`,
`excluded_sections`, `safe_failure_reason`, `requested_at`, `completed_at`,
`expires_at`.

**Relationships**: Owns inspection access audit events and references existing
artifact metadata for object storage.

**Validation rules**: Only administrators and auditors can export within
tenant scope. Export content is serialized through the same viewer-aware
redaction layer as API responses.

**State transitions**: `requested` -> `generating`; `generating` ->
`available`; `generating` -> `failed`; `available` -> `expired`;
`available` -> `revoked`.

## RedactionClassificationRecord

Append-only metadata for classification and redaction policy decisions.

**Fields**: `redaction_classification_record_id`, `tenant_id`,
`source_record_type`, `source_record_id`, `classification_version`,
`field_name`, `sensitivity_label`, `redaction_action`, `viewer_role`,
`decision_reason`, `created_at`.

**Relationships**: May be referenced by API serializers and export manifests.

**Validation rules**: Unknown dynamic fields default to redacted summary.
Changes in classification are represented by new records, not updates.
