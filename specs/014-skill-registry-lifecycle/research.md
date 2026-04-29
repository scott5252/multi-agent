# Research: Skill Registry And Installation Lifecycle

## Declarative V1 Skill Packages

**Decision**: V1 skill packages are declarative manifests with safe
documentation, fixtures, compatibility metadata, and references to existing
approved tool/MCP integrations only.

**Rationale**: The current platform already governs tool access through
model_skill_config skill bindings, allowed tool policies, outbound domain
policies, credential requirements, and runtime policy decisions. Reusing that
surface gives admins a registry lifecycle without introducing executable
package runtimes, unbounded network surfaces, or a second tool authorization
system.

**Alternatives considered**: Executable Python packages, standalone external
HTTP skill services, and arbitrary MCP server definitions were rejected for
this feature because they require sandboxing, supply-chain controls, network
containment, runtime package loading, and operational controls beyond the
current declarative requirement.

## Package Artifact Storage

**Decision**: Store published package artifacts, pinned manifests, safe docs,
fixtures, and oversized validation evidence in object storage. Store
transactional metadata, artifact handles, media types, sizes, checksums,
digests, lifecycle state, and audit links in PostgreSQL.

**Rationale**: The constitution requires PostgreSQL to remain the source of
truth for lifecycle state while object storage carries large payloads. The
existing artifact metadata model and storage providers already support
provider, key, checksum, retention class, and tenant/global scope metadata.

**Alternatives considered**: Storing artifact bytes in PostgreSQL was rejected
as blob storage. Storing only remote URLs was rejected because publication
must lock internal artifact provenance and digests for future validation,
installation, audit, and readiness checks.

## Manifest Schema And Validation

**Decision**: Define a Pydantic v2 manifest schema with required slug,
semantic version, description, entrypoint type, tool declarations, action
categories, network requirements, credential requirements, runtime
permissions, test fixtures, compatibility metadata, safe documentation, and
artifact/documentation digests.

**Rationale**: A typed schema gives deterministic validation, clear API
contracts, stable digest generation, and actionable admin findings. It also
lets workflow publish validation compare installed-skill manifests against
known tool/action/policy vocabulary.

**Alternatives considered**: Accepting opaque JSON was rejected because it
would make policy integration and validation ad hoc. Deferring validation to
runtime was rejected because invalid or unsafe packages must be blocked before
publication or tenant installation.

## Publication And Immutability

**Decision**: Platform admins publish immutable `skill_package_versions` after
successful validation. A unique `(package_id, semantic_version)` constraint
prevents duplicate versions. Any manifest, docs, fixtures, permissions,
compatibility, or entrypoint change requires a new version.

**Rationale**: Skill behavior must be stable for tenant installations, workflow
publish validation, runtime pinning, audit, replay, and incident analysis.

**Alternatives considered**: Mutable package versions were rejected because
existing bindings could change behavior silently. Using latest-version aliases
for runtime use was rejected because Spec 007 bindings require exact skill
version evidence.

## Tenant Installations And Readiness

**Decision**: Tenant installs create immutable installation versions that pin
the exact package version and manifest digest. Mutable readiness projections
track credential status, smoke-test status, compatibility status, policy
status, binding eligibility, quarantine, and findings behind optimistic
concurrency tokens.

**Rationale**: Installations need durable, auditable evidence while allowing
admins to configure credentials and rerun smoke tests. Optimistic concurrency
prevents stale readiness, credential, and binding updates from silently
overwriting newer decisions.

**Alternatives considered**: Mutating a single installation row in place was
rejected because upgrade lineage and pinned workflow behavior would be hard to
audit. Locking rows for long admin sessions was rejected because stale form
writes should fail cleanly without holding database locks.

## Smoke Test Runner

**Decision**: Run package-declared smoke tests through isolated,
tenant-scoped jobs that use safe fixtures, existing secret references or
delegated credentials, Spec 007 tool/domain/credential policy preview, and
existing reliability admission, retry, breaker, and artifact I/O controls.

**Rationale**: Smoke tests prove installation readiness without expanding
runtime privileges. The runner can execute safe tool/MCP probes under the same
policy rules that runtime use will face and persist evidence without raw
credential values.

**Alternatives considered**: Running smoke tests synchronously in admin
requests was rejected because external tool probes and object storage may be
slow or retryable. Running tests with platform-level credentials was rejected
because tenant readiness must be tenant-specific.

## Spec 007 Policy Integration

**Decision**: Installed skills become eligible for Spec 007 skill bindings
only when the installation is ready, tenant-visible, non-quarantined,
policy-compatible, and pinned to exact package artifact and manifest digests.
Binding preview and workflow publish validation call the existing
model_skill_config policy preview/resolver and include installation ids and
manifest evidence.

**Rationale**: The registry should supply trustworthy inventory and readiness
evidence; Spec 007 remains the authority for binding and runtime policy
decisions. This keeps one source of truth for tool allowlists, outbound
domains, secret references, and credential requirements.

**Alternatives considered**: Creating a new binding table in the registry was
rejected because it would fork policy semantics. Treating package availability
as binding eligibility was rejected because tenant credentials, smoke tests,
compatibility, quarantine, and policy scope can differ per installation.

## Upgrade, Rollback, Withdrawal, And Quarantine

**Decision**: Upgrades install a newer package version as a new immutable
installation version. Rollback is explicit rebinding or workflow publication
to a prior eligible installation. Withdrawal blocks new installs but preserves
existing use. Quarantine blocks new installs, readiness promotion, new
bindings, workflow publish, and runtime use for affected package versions or
installations until resolved.

**Rationale**: This preserves version-pinned runtime behavior while giving
operators safety controls when a package or installation is later found
unsafe.

**Alternatives considered**: Auto-upgrading bindings was rejected because it
can change runtime behavior without admin intent. Deleting unsafe records was
rejected because audit, incident response, and replay need immutable history.

## Admin Experience

**Decision**: Provide server-rendered admin pages plus JSON APIs for package
publication, version detail, tenant availability, tenant discovery,
installation configuration, smoke-test execution, readiness, binding
eligibility, upgrade lineage, quarantine, and audit review.

**Rationale**: The existing admin shell is the established surface for
non-developer operators and already carries scope selection, authorization,
safe empty/error states, and template testing patterns.

**Alternatives considered**: Building a separate frontend was rejected as
unnecessary scope. Providing APIs only was rejected because package publication
and tenant readiness are operator workflows that need guided visibility.

## Audit, Redaction, And Exports

**Decision**: Persist `skill_audit_records` as safe, append-only lifecycle
events and reuse existing redaction/classification helpers for views and
exports. Audit payloads include actor, scope, tenant, package slug/version,
installation version, outcome, safe findings, policy ids, and trace ids, never
raw secrets or unsafe package payloads.

**Rationale**: Governance and incident response require end-to-end evidence
from publication through runtime eligibility while protecting credential and
package-sensitive data.

**Alternatives considered**: Relying only on generic audit records was
rejected because skill lifecycle queries need package, installation, test, and
binding dimensions. Storing raw validation input in audit was rejected because
package docs and fixtures may later be classified unsafe.
