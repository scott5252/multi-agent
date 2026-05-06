# Spec 038 Reviewer Notes

## Summary

Spec 038 adds a deletion-grade Jinja surface inventory without deleting any Jinja template, route, helper, static asset, import, or fallback.

The implementation introduces a deterministic scanner, backend-owned schema, protected JSON route, generated React contracts, React migration dashboard panel, focused tests, QA documents, and generated inventory evidence at `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`.

## Inventory Snapshot

- Total inventory items: 533.
- Templates: 160.
- Browser-rendering routes and route references: 182.
- Legacy static JavaScript and CSS assets: 9.
- Docs and QA direct links: 157.
- Blocked items: 33.
- Items marked safe to delete: 0.

## Reviewer Decision

No deletion is approved by this spec.

Every inventory item remains retained until its bounded follow-up spec proves redirect, compatibility response, tenant isolation, redaction, direct-link, mutation, export, upload, SSE, artifact, denied-state, and Playwright parity.

Reviewer signoff is required before any later spec changes an item from retained to safe-to-delete.

## Scope Notes

- Spec 039 owns shell, auth, saved filters, and React host inventory.
- Spec 040 owns workflow registry, builder, validation, publish, and workflow-route inventory.
- Spec 041 owns model provider, prompt, profile, and governance inventory.
- Spec 042 owns skill registry and skill execution inventory.
- Spec 043 owns agent and workflow test bench inventory.
- Spec 044 owns platform operations, reliability, usage, and admin run inventory.
- Spec 045 owns channels, Telegram, briefing, memberships, and people-oriented inventory.
- Spec 046 owns user-facing `/runs` direct-link and compatibility inventory.
- Spec 047 owns final Jinja infrastructure, imports, template provider, and dependency retirement inventory.

## Redaction Notes

The scanner and dashboard use repo-relative paths and safe evidence identifiers.

The QA redaction sweep checks for local absolute paths, raw secrets, raw prompts, raw completions, memory content, private channel messages, raw run payloads, stack traces, and unauthorized tenant labels.

The intentionally unsafe marker `qa038-secret-value` is rejected by schema and test evidence.

## Tenant Notes

Platform service tests prove platform-only groups are present in the full inventory projection.

Tenant route tests prove Acme tenant administrators can retrieve tenant-safe inventory and receive a fail-closed response when requesting Globex scope.

Tenant-scoped inventory omits platform-only Spec 044 surfaces.

## Validation Notes

Focused checks already cover:

- `tests/unit/admin/test_jinja_inventory_scanner.py`
- `tests/unit/admin/test_migration_hardening_service.py`
- `tests/unit/api/test_admin_migration_hardening_react_schema.py`
- `tests/contract/test_admin_migration_jinja_inventory_contract.py`
- `tests/contract/test_admin_react_contract.py`
- `tests/integration/api/test_admin_react_migration_inventory_routes.py`
- `frontend/admin/src/components/migrationHardening/JinjaInventoryPanel.test.tsx`
- `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.test.tsx`
- `frontend/admin/src/App.test.tsx`

Final validation must still run the generated QA document validator, API/database/quality runner, and Playwright runner before Spec 039 begins.
