# Research: Jinja Surface Inventory And Deletion Plan

## Decision: Scanner Output Uses Repo-Relative Evidence

**Rationale**: Absolute local paths are sensitive and are explicitly banned from UI, exports, screenshots, QA artifacts, logs, and docs. Repo-relative paths plus line numbers give reviewers enough precision without leaking workstation details.

**Alternatives considered**:

- Persist absolute paths. Rejected for redaction and portability.
- Store only counts. Rejected because later deletion specs need item-level evidence.

## Decision: Inventory Lives In The Existing Migration Dashboard

**Rationale**: Spec 037 already established `/admin/app/migration` as the route parity and rollback ledger. Adding the Jinja inventory there keeps reviewers in one protected React workspace and avoids another migration console.

**Alternatives considered**:

- Create a new `/admin/app/jinja-inventory` page. Rejected because it splits the deletion review workflow.
- Write only JSON evidence. Rejected because browser-first QA requires visible reviewer evidence.

## Decision: Classification Is Conservative

**Rationale**: Spec 038 is not allowed to delete Jinja files. The scanner may identify candidates, but any uncertain item must be `react_parity_missing`, `non_jinja_compatibility_needed`, or `blocked_with_reason`. `safe_to_delete` requires explicit parity evidence and reviewer signoff requirement.

**Alternatives considered**:

- Infer safe deletion from route naming alone. Rejected because direct links, forms, exports, uploads, and denied states can live behind the same route prefix.

## Decision: User-Facing `/runs`, Local Login, And React Host Are In Scope

**Rationale**: Complete Jinja removal includes server-rendered user channel pages, auth utility pages, and the current React app host. They must be inventoried before later specs can convert or retire them safely.

**Alternatives considered**:

- Admin-only inventory. Rejected because it would miss `/runs` and auth utility Jinja surfaces.

## Decision: No New Durable Tables

**Rationale**: Inventory is deterministic repository evidence for a migration phase, not mutable operational state. Generated JSON and dashboard projections are sufficient and avoid schema churn.

**Alternatives considered**:

- Add PostgreSQL tables for inventory. Rejected as unnecessary persistence and migration overhead for a repo-scanned ledger.

## Decision: Static Vite HTML Remains Allowed

**Rationale**: The removal target is server-side Jinja rendering. React built assets and static HTML can remain as non-Jinja browser delivery mechanisms.

**Alternatives considered**:

- Ban all HTML files. Rejected because Vite/static app delivery is the intended replacement route.
