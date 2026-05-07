# PR Notes: Spec 042

## Summary

- Moves skill registry and SkillExecutionGateway diagnostics browser journeys to React-admin routes under `/admin/app/skills`.
- Converts old skill registry and diagnostics browser routes to authenticated redirects or safe non-Jinja problem responses.
- Deletes skill-owned Jinja templates and adds scanner tests proving routers no longer render them.
- Adds backend, contract, docs, generated type, and React component coverage for legacy route evidence and redaction-safe skill lifecycle data.

## Validation

- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy src`
- `uv run pytest --no-cov tests/integration/api/test_admin_skill_registry_legacy_redirects.py tests/integration/api/test_admin_skill_registry_browser_flows.py tests/integration/api/test_admin_skill_execution_legacy_redirects.py tests/integration/api/test_admin_skill_execution_ui.py tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py tests/unit/admin/test_skill_jinja_retirement.py tests/unit/api/test_admin_skill_lifecycle_schema.py tests/docs/test_skill_registry_docs.py`
- `cd frontend/admin && npm test -- --run src/components/skills src/App.test.tsx`
- `cd frontend/admin && npm run build`

## Reviewer Focus

- Verify old `/admin/skill-registry/ui/*` URLs redirect to `/admin/app/skills/*`.
- Verify old `/admin/skill-execution/ui/diagnostics` redirects to `/admin/app/skills/diagnostics`.
- Verify React skill lifecycle payloads contain safe summaries, fingerprints, audit references, and artifact references, not raw manifests or credentials.
- Verify tenant-scoped routes fail closed and do not reveal unauthorized tenant labels.
