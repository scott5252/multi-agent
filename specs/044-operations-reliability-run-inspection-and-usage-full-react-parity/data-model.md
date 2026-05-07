# Data Model: Operations, Reliability, Run Inspection, And Usage Full React Parity

## OperationsReactWorkspace

- **Fields**: active scope, health summaries, reliability cards, queue metrics,
  provider/channel status, run-debug summaries, usage summaries, export action,
  audit references, navigation links.
- **Validation**: scope comes from backend shell context; metrics are bounded
  and redacted; links are authorized.

## ReliabilityActionSummary

- **Fields**: action id, label, target kind, target reference, eligibility,
  required role, side-effect posture, idempotency requirement, safe reason,
  remediation, audit reference.
- **Validation**: action appears only when backend policy permits it for the
  current principal and scope.

## ReliabilityMutationResult

- **Fields**: mutation id, status, target summary, accepted/denied/queued
  message, retry schedule summary, audit reference, redaction status.
- **Validation**: never echoes raw dead-letter payloads, stack traces, request
  bodies, provider responses, or private labels.

## RunInspectionSummary

- **Fields**: run id, tenant scope, workflow label, status, actor summary,
  started/finished labels, usage, latency, detail href, audit reference.
- **Validation**: run lists are bounded and tenant-filtered.

## RunDebugEnvelope

- **Fields**: run status, timeline events, replay references, lineage summary,
  bundle snapshot metadata, approvals, usage, artifacts, errors, audit records,
  redaction evidence.
- **Validation**: raw prompts, completions, memory, tool payloads, private
  messages, and stack traces are summarized or omitted.

## UsageExportDetail

- **Fields**: export id, tenant scope, status, filter snapshot, requested by,
  row count, checksum, artifact reference id, retention state, audit reference,
  safe problem state.
- **Validation**: raw CSV rows and storage paths are never rendered.

## LegacyOperationsRouteRecord

- **Fields**: legacy method, legacy path, destination, preserved query keys,
  required permission/role, retirement behavior, audit label.
- **Validation**: unsafe query values and unauthorized ids fail closed.

## OperationsAuditRecord

- **Fields**: actor summary, tenant scope, action, target summary, outcome,
  redaction status, timestamp label, audit reference.
- **Validation**: event summaries are safe for screenshots and QA artifacts.
