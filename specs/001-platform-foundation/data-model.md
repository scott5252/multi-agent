# Data Model: Platform Foundation

## Overview

The platform foundation introduces the minimum durable entities needed to boot a
tenant-aware API service, run a worker shell, validate migrations, record audit
events, resolve secrets by reference, and keep large payload metadata out of
the transactional hot path.

Alembic's internal version table is implementation-managed and is not treated
as a domain entity here.

## Core Entities

### Tenant

| Field | Type | Notes |
|---|---|---|
| `tenant_id` | UUID | Primary key |
| `slug` | text | Lowercase, unique, URL-safe identifier |
| `display_name` | text | Human-readable name |
| `status` | enum | `active`, `suspended` |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last metadata update |

**Validation rules**

- `slug` is globally unique and normalized to lowercase kebab-case.
- Only `active` tenants may own new tenant-scoped jobs or artifacts.

**Relationships**

- One tenant has many limit policies, queue jobs, artifacts, secret references,
  and audit events.

### TenantLimitPolicy

| Field | Type | Notes |
|---|---|---|
| `policy_id` | UUID | Primary key |
| `tenant_id` | UUID | FK to `Tenant` |
| `max_concurrent_jobs` | integer | Positive |
| `max_api_rps` | integer | Positive |
| `max_artifact_bytes` | bigint | Positive |
| `enabled` | boolean | Feature toggle for the policy row |
| `effective_from` | timestamptz | Start of policy validity |

**Validation rules**

- Numeric limits must be positive integers.
- Only one enabled policy should be effective for a tenant at a point in time.

### QueueJob

| Field | Type | Notes |
|---|---|---|
| `job_id` | UUID | Primary key |
| `tenant_id` | UUID nullable | Required for tenant-scoped jobs |
| `scope_type` | enum | `tenant`, `platform` |
| `job_kind` | enum | `bootstrap_task`, `migration_task`, `runtime_task` |
| `payload_json` | JSONB | Small durable payload metadata only |
| `artifact_id` | UUID nullable | Optional FK to `ArtifactRecord` for large payload indirection |
| `status` | enum | `pending`, `leased`, `completed`, `failed`, `dead_letter` |
| `priority` | smallint | Lower value = higher dispatch priority |
| `available_at` | timestamptz | Earliest lease time |
| `attempt_count` | integer | Retry counter |
| `max_attempts` | integer | Retry ceiling |
| `idempotency_key` | text | Logical deduplication key |
| `trace_id` | text | Correlation ID |
| `run_id` | text nullable | Reserved for future runtime lineage |
| `parent_run_id` | text nullable | Reserved for future parent-child lineage |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last mutation timestamp |
| `completed_at` | timestamptz nullable | Completion timestamp |

**Validation rules**

- `tenant_id` is required when `scope_type = tenant`.
- Platform-scoped jobs must run under explicit system context and must not use a
  default tenant.
- `idempotency_key` must be unique for the logical dispatch boundary.

**State transitions**

- `pending -> leased`
- `leased -> completed`
- `leased -> failed`
- `failed -> pending`
- `failed -> dead_letter`

### JobLease

| Field | Type | Notes |
|---|---|---|
| `lease_id` | UUID | Primary key |
| `job_id` | UUID | FK to `QueueJob` |
| `worker_id` | text | Stable worker/process identifier |
| `acquired_at` | timestamptz | Lease start |
| `heartbeat_at` | timestamptz | Last heartbeat |
| `expires_at` | timestamptz | Lease expiry |
| `released_at` | timestamptz nullable | Release timestamp |

**Validation rules**

- `expires_at` must be greater than `acquired_at`.
- Only one active lease exists per job.

**State transitions**

- `active -> released`
- `active -> expired`

### ArtifactRecord

| Field | Type | Notes |
|---|---|---|
| `artifact_id` | UUID | Primary key |
| `tenant_id` | UUID nullable | Required for tenant-scoped artifacts |
| `scope_type` | enum | `tenant`, `platform` |
| `storage_provider` | enum | `filesystem`, `s3` |
| `storage_uri` | text | External object location |
| `content_type` | text | MIME type |
| `byte_size` | bigint | Positive |
| `sha256` | text | Integrity hash |
| `retention_class` | enum | `ephemeral`, `standard`, `audit` |
| `status` | enum | `pending`, `available`, `deleted`, `expired` |
| `created_by_job_id` | UUID nullable | Optional provenance FK |
| `created_at` | timestamptz | Creation timestamp |
| `expires_at` | timestamptz nullable | Optional retention deadline |

**Validation rules**

- `sha256` is required before `status = available`.
- Large payloads use `storage_uri`; PostgreSQL stores only metadata.

**State transitions**

- `pending -> available`
- `available -> deleted`
- `available -> expired`

### SecretReference

| Field | Type | Notes |
|---|---|---|
| `secret_reference_id` | UUID | Primary key |
| `tenant_id` | UUID nullable | Nullable for platform-scoped secrets |
| `scope_type` | enum | `platform`, `tenant`, `user_delegated` |
| `provider` | enum | `env`, `aws_sm`, `gcp_sm`, `vault` |
| `external_name` | text | Lookup key in the provider |
| `access_policy` | JSONB | Redacted policy metadata only |
| `status` | enum | `active`, `revoked` |
| `created_at` | timestamptz | Creation timestamp |
| `updated_at` | timestamptz | Last metadata update |

**Validation rules**

- Secret material is never stored in this table.
- `scope_type = tenant` requires `tenant_id`.
- Local and test stand-ins still resolve through the same provider interface.

### AuditEvent

| Field | Type | Notes |
|---|---|---|
| `audit_event_id` | UUID | Primary key |
| `tenant_id` | UUID nullable | Required for tenant scope |
| `scope_type` | enum | `platform`, `tenant` |
| `actor_type` | enum | `system`, `service`, `user` |
| `actor_id` | text | Actor identifier |
| `action` | text | Audited action |
| `entity_type` | text | Entity kind |
| `entity_id` | text | Entity identifier |
| `trace_id` | text | Correlation ID |
| `request_id` | text nullable | HTTP correlation when present |
| `payload_redacted` | JSONB | Secret-free audit payload |
| `occurred_at` | timestamptz | Event timestamp |

**Validation rules**

- Audit payloads must not contain secret values.
- Tenant-scoped events require `tenant_id`.

## Supporting Non-Persistent Models

### PlatformProcessProfile

A code-level model that describes the operating mode for a process:

- `process_role`: `api`, `worker`, `cli`
- `required_dependencies`
- `readiness_policy`
- `scope_type`

### ScopeContext

A request or worker scoped model that carries:

- `scope_type`
- `tenant_id` (nullable only for explicit platform scope)
- `trace_id`
- `request_id`
- `principal_id`

### DependencyHealthCheck

The response model for readiness and dependency-status checks:

- `name`
- `required`
- `status`
- `detail`
- `checked_at`

## Relationship Summary

- `Tenant 1 -> N TenantLimitPolicy`
- `Tenant 1 -> N QueueJob`
- `Tenant 1 -> N ArtifactRecord`
- `Tenant 1 -> N SecretReference`
- `Tenant 1 -> N AuditEvent`
- `QueueJob 1 -> 0..1 active JobLease`
- `QueueJob 1 -> 0..N AuditEvent`
- `QueueJob 1 -> 0..N ArtifactRecord`

## Notes For Planning

- Queue, audit, and artifact entities intentionally reserve `trace_id`,
  `run_id`, and `parent_run_id` extension points so future runtime and lineage
  work does not require disruptive schema changes.
- Artifact and secret entities model metadata and references only. They do not
  store blob content or secret material.
