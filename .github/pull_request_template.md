## Summary

- Describe the feature or operational change.

## Validation

- [ ] `uv sync`
- [ ] `./scripts/check.sh`
- [ ] `./scripts/smoke_foundation.sh` against a running API when runtime code changed

## Review Checklist

- [ ] Tenant isolation rules are preserved or updated intentionally
- [ ] Secret values are not written to logs, audit payloads, or persisted data
- [ ] Migration upgrade and downgrade expectations were validated
- [ ] Readiness behavior is documented when dependencies or migrations are unavailable
- [ ] Updated docs cover setup, troubleshooting, and recovery impact
