# PR Review Notes: Production Audit And Debugging

## Scope

This change adds append-only audit timeline storage, runtime trace records,
capture gaps, inspection access audits, version-bundle snapshots, lineage
links, notification and secret-access metadata surfaces, redacted export
metadata, classification/redaction helpers, admin APIs, minimal admin views,
and observability helpers.

## Timeline Completeness

Lifecycle builders cover accepted, queued, started, waiting, resumed, retried,
completed, cancelled, failed, and timed-out states. Runtime decision helpers
cover handoffs, contract validations, memory writes, tool usage, model
selection, notifications, secret access, and diagnostic capture gaps.

## Authorization

Inspection, search, replay, lineage, bundle, and export service methods require
administrator or auditor roles and tenant scope. Denied attempts create
inspection access audit events before returning safe failures where possible.

## Redaction And Secret Hygiene

Classification defaults unknown dynamic fields to redaction. Review evidence
contains no raw secrets, credentials, provider tokens, unauthorized prompt
text, or unauthorized memory content. Logs, metrics, timelines, traces,
exports, README guidance, and these PR notes use safe identifiers, counts,
digests, categories, and summaries.

## Version Bundles And Lineage

Pinned bundle snapshots expose digest and version references only. Lineage
graphs include redacted boundary nodes for unauthorized related runs.

## Notification And Secret Evidence

Notification traces expose delivery state and provider correlation references
without unrestricted destinations. Secret-access audits expose requester and
reference metadata without values.

## Operational Risk

Security and governance capture is fail-closed. Diagnostic gaps are explicit
unavailable markers. Exports are metadata-first and idempotent for repeated
requests from the same actor and scope.

## Coverage Evidence

Focused unit and contract tests cover schemas, classification, capture,
inspection, repository behavior, replay assembly, export metadata, and
observability helpers. Full quality gates are recorded in
`testing-instructions.md`.
