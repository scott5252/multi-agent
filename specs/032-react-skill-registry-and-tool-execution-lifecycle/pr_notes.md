# PR Notes: React Skill Registry And Tool Execution Lifecycle

## Summary

Implemented an additive React skill lifecycle workspace at `/admin/app/skills`.

The backend adds safe skill lifecycle schemas, deterministic aggregation
builders, protected React routes, policy surface entries, generated TypeScript
contracts, and focused unit/integration/performance coverage.

The frontend adds a browser-first skill lifecycle page with platform package
publication, tenant discovery and installation, credential reference
configuration, queued smoke-test/readiness refresh, connector readiness,
SkillExecutionGateway diagnostics, binding eligibility preview, and audit
timeline sections.

Existing Jinja skill registry and skill execution diagnostic routes remain
available.

## Safety Notes

- Raw manifests are not echoed after candidate submission.
- Upload metadata takes precedence over pasted manifest text.
- Credential values and authorization headers are never returned to React.
- Connector diagnostics are safe summaries and evidence references.
- Binding eligibility preview is read-only and does not execute live tools.
- Platform package publication, tenant grant mutation, quarantine, and
  withdrawal are platform-admin only.
- Tenant discovery, installation, credentials, readiness, diagnostics,
  binding, and audit routes fail closed for cross-tenant access.

## Validation

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_skill_lifecycle_schema.py \
  tests/unit/admin/test_skill_lifecycle_service.py \
  tests/performance/skills/test_skill_lifecycle_queries.py \
  tests/contract/test_admin_react_contract.py \
  tests/integration/test_admin_react_routes.py
```

Result: passed, 33 tests.

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Result: passed.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

Result: passed.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml
```

Result: passed after QA032 database reset, curl/API checks, QA document
validation, Ruff, format, mypy, full coverage, focused backend tests, frontend
typecheck/tests/build, and generated contract drift check.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml --start-processes
```

Result: passed.

## QA Evidence

- `output/playwright/qa032_ui/qa032-react-skills-denied.png`
- `output/playwright/qa032_ui/qa032-react-skills-platform.png`
- `output/playwright/qa032_ui/qa032-react-skills-publication.png`
- `output/playwright/qa032_ui/qa032-react-skills-tenant.png`
- `output/playwright/qa032_ui/qa032-react-skills-credential.png`
- `output/playwright/qa032_ui/qa032-react-skills-readiness.png`
- `output/playwright/qa032_ui/qa032-react-skills-diagnostics.png`
- `output/playwright/qa032_ui/qa032-react-skills-binding.png`
- `output/playwright/qa032_ui/qa032-react-skills-audit.png`
- `output/playwright/qa032_ui/qa032-react-skills-cross-tenant.png`

Redaction scan:

```bash
rg -n "qa032-secret-value|raw manifest|resolved credential|authorization header|provider token|private message|connector request|connector response|raw tool output|stack trace|/Users/|Globex" /tmp/qa032-* output/playwright/qa032_ui || true
```

Result: no matches.

## Reviewer Checklist

- Confirm platform-only publication and grant mutation controls.
- Confirm tenant-only discovery, installation, credential, and readiness flows.
- Confirm generated TypeScript contracts are current.
- Confirm no screenshots or JSON evidence include unsafe text.
- Confirm existing Jinja routes still render.
