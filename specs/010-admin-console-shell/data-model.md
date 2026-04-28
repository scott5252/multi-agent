# Data Model: Admin Console Shell

**Feature**: Admin Console Shell
**Date**: 2026-04-27

## Overview

The shell is mostly request-derived UI state. The only new persisted domain
state is saved filters, because the specification requires useful filters to be
restored server-side by user, admin area, and platform or tenant scope. Access
decisions and audit evidence reuse existing access/audit tables with
shell-specific actions and safe payloads.

## Persisted Entity

### Admin Saved Filter

Server-persisted, user- and scope-bound filter criteria for a filterable admin
page.

- `admin_saved_filter_id`: UUID primary key
- `principal_identity_id`: UUID, references `principal_identities`
- `principal_id`: string fallback for local/system evidence when an identity
  record is not yet available
- `admin_area`: string enum value:
  `workflows`, `model_skill_history`, `run_inspection`,
  `reliability_breakers`, `reliability_dead_letters`
- `filter_key`: stable page/filter identifier within the admin area
- `scope_type`: `platform` or `tenant`
- `tenant_id`: nullable UUID; required when `scope_type` is `tenant`, null
  when `scope_type` is `platform`
- `display_name`: safe user-visible name, max 120 characters
- `criteria`: JSON object containing normalized validated criteria only
- `safe_summary`: JSON object with safe labels for review/restore UI
- `criteria_schema_version`: string, initial value `2026-04-27`
- `last_restored_at`: nullable timestamp
- `created_at`, `updated_at`: timestamps

Validation rules:

- Unique active filter per `(principal_identity_id, admin_area, filter_key,
  scope_type, tenant_id, display_name)`.
- `tenant_id` must be null for platform scope and non-null for tenant scope.
- `tenant_id` must be authorized for the principal before save or restore.
- Every criterion must be whitelisted for the admin area's filter profile.
- Unsupported, malformed, expired, unauthorized, or scope-mismatched criteria
  are rejected on save and dropped or rejected on restore before query
  execution.
- `criteria` and `safe_summary` must not contain raw secrets, credentials,
  protected prompt content, protected memory content, raw run payloads, stack
  traces, or cross-tenant labels.
- Updating a saved filter overwrites the validated criteria and updates
  `updated_at`; it does not mutate audit/access records.

Indexes:

- `(principal_identity_id, admin_area, scope_type, tenant_id, updated_at)` for
  listing filters in the current scope.
- `(principal_identity_id, admin_area, filter_key, scope_type, tenant_id)` for
  restore lookup.

## Reused Existing Entities

### Principal Identity And Role Grant

Existing `principal_identities` and `role_grants` identify the actor and
available platform/tenant scopes. Platform admins can operate in platform
scope and enter tenant-scoped destinations only when authorized. Tenant admins
can operate only in validated tenant scopes.

### Access Decision Record

Existing `access_decision_records` continue to store direct route access
decisions. Shell routes add policy surfaces for landing, scope selection,
model-skill UI pages, and saved-filter actions.

### Audit Event

Existing `audit_events` store shell-specific evidence for navigation
visibility, scope selection, and saved-filter restoration. Payloads are
redacted and itemized where required.

## Non-Persisted View Models

The following models are request-scoped Pydantic/dataclass view models and do
not require database tables:

- `AdminShellContext`
- `AdminScope`
- `AdminScopeOption`
- `NavigationGroup`
- `NavigationItem`
- `NavigationOutcome`
- `BreadcrumbItem`
- `PageAction`
- `FlashMessage`
- `CommonState`
- `SavedFilterSummary`
- `ShellWrappedPage`

These models are rebuilt per request from the principal, active scope,
navigation registry, page builder, saved-filter repository, and authorization
decisions.

## State Transitions

### Saved Filter

```text
missing -> saved -> restored
saved -> updated -> restored
saved -> deleted
saved -> restore_dropped_criteria -> restored
saved -> restore_denied
```

- `save` validates all criteria and writes only normalized safe values.
- `restore` revalidates scope and criteria before applying any filter.
- `restore_dropped_criteria` records safe audit evidence and applies only the
  remaining authorized criteria.
- `restore_denied` records a safe denied/unavailable decision and does not
  apply the filter.

## Migration

Add `alembic/versions/0010_admin_console_shell.py` to create
`admin_saved_filters` with foreign keys to `principal_identities` and
`tenants`, scoped indexes, timestamp columns, and JSON criteria/summary
columns. No schema change is required for request-scoped shell view models.
