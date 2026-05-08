# Data Model: Skill Lifecycle React Live Data

## Skill Package Projection

- Source: persisted skill package and package version records.
- Fields: package id, slug, display name, lifecycle state, latest version, safe manifest summary, validation evidence reference, smoke evidence reference, quarantine summary, withdrawal summary, tenant grant summary, authorized actions, audit reference.
- Empty state: no authorized package records exist for the active scope.
- Redaction: raw manifest content and validation transcripts never appear.

## Package Candidate Projection

- Source: persisted candidate, validation, artifact, and publication readiness records.
- Fields: candidate id, package slug, revision token, manifest digest, source label, safe manifest summary, validation status, validation findings, safe documentation summary, smoke evidence status, publish blockers, authorized actions.
- State transitions: created, validation unavailable, validation passed, validation failed, publish blocked, published, stale conflict.
- Redaction: uploaded manifest bodies and raw validation findings are summarized.

## Tenant Grant Projection

- Source: package tenant grant and tenant availability records.
- Fields: tenant id, tenant label, package slug, version label, grant status, allowed versions, install eligibility, restrictions, authorized actions.
- State transitions: available, restricted, revoked, withdrawn, quarantined.
- Tenant isolation: tenant users see only grants for their active tenant; platform admins see authorized grant summaries without private tenant labels beyond safe labels.

## Skill Installation Projection

- Source: tenant skill installation records and package version references.
- Fields: installation id, package id, package slug, version label, installation status, revision token, credential readiness, smoke-test readiness, connector readiness summary, binding readiness, authorized actions, audit reference.
- State transitions: installable, installing, ready, degraded, blocked, uninstalled, stale conflict.
- Redaction: credential values and connector payloads never appear.

## Credential Readiness Projection

- Source: installation credential reference metadata and readiness checks.
- Fields: reference id, label, source type, readiness, fingerprint, policy reason, last checked label, remediation.
- State transitions: unconfigured, ready, warning, blocked, unavailable.
- Redaction: only reference ids, fingerprints, and safe remediation text render.

## Smoke-Test Evidence Projection

- Source: package or installation smoke-test records and safe artifact metadata.
- Fields: test id, execution mode, status, safe summary, artifact reference, audit reference, started/completed labels, remediation.
- State transitions: queued, running, passed, failed, stale, unavailable.
- Redaction: raw transcripts and connector responses remain outside React.

## Connector Diagnostic Projection

- Source: SkillExecutionGateway summaries, governed connector diagnostics, policy decisions, and audit records.
- Fields: diagnostic id, connector id, connector label, tool names, outbound policy status, credential policy status, connector readiness, safe summary, evidence reference, audit reference.
- State transitions: ready, degraded, blocked, unavailable.
- Redaction: raw connector request/response, tool output, and private channel content never render.

## Binding Eligibility Projection

- Source: package version, tenant grant, installation, credential readiness, connector readiness, and model-skill policy records.
- Fields: preview id, workflow context label, package id, profile id, eligibility status, allowed tools, blocked tools, policy reasons, audit reference.
- State transitions: ready, blocked, denied, unavailable.
- Redaction: workflow context is a safe label only, not a raw workflow document or prompt.

## Lifecycle Audit Projection

- Source: append-only skill audit records.
- Fields: record id, timestamp label, actor label, action, package slug, tenant scope label, outcome, safe summary, audit reference.
- Bounds: latest records are limited to a fixed page size.
- Redaction: actor and tenant labels are safe summaries; unauthorized tenant labels do not render.
