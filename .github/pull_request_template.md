## Summary

- Describe the feature or operational change.

## Validation

- [ ] `uv sync`
- [ ] `./scripts/check.sh`
- [ ] `./scripts/smoke_foundation.sh` against a running API when runtime code changed
- [ ] `uv run pytest tests/contract/test_access_control_contract.py tests/integration/api/test_auth_routes.py tests/integration/auth/test_support_overrides.py`
- [ ] Workflow-registry validation and UI slice was run when admin workflow code changed

## Review Checklist

- [ ] Tenant isolation rules are preserved or updated intentionally
- [ ] Secret values are not written to logs, audit payloads, or persisted data
- [ ] Auth mode changes preserve production Auth0 requirements and non-production local-principal guardrails
- [ ] Support overrides require a second approver and remain auditable
- [ ] Delegated credentials remain tool-scoped and secret-free in audit data
- [ ] Migration upgrade and downgrade expectations were validated
- [ ] Readiness behavior is documented when dependencies or migrations are unavailable
- [ ] Updated docs cover setup, troubleshooting, and recovery impact
- [ ] Workflow-registry changes include validation, publish, and sharing evidence
- [ ] Workflow-registry UI changes include updated route or HTML verification evidence
