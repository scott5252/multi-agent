# Data Model: Jinja Infrastructure Decommission

## Decommission Evidence

- **Fields**: evidence id, label, status, checked artifact count, unsafe match count, evidence reference, safe summary.
- **Rules**: Evidence references are repository-relative identifiers or QA artifact ids, never absolute local paths.
- **Source**: Scanner tests, route tests, dependency scans, frontend tests, Spec QA, Playwright, redaction and tenant sweeps.

## Runtime Import Scan

- **Fields**: scan id, scanned roots, forbidden symbols, excluded generated/static paths, result count, evidence reference.
- **Forbidden Symbols**: `jinja2`, `Jinja2Templates`, `TemplateResponse`, `workflow_ui_templates`.
- **Rules**: Runtime source under `src/multi_agent_platform` is authoritative; tests and historical specs may mention removed symbols only as evidence.

## Compatibility Redirect

- **Fields**: legacy route, React route, status code, preserved query keys, scope requirement, authorization mode, audit reference.
- **Rules**: Redirects preserve tenant id and safe route parameters only. Unsafe arbitrary query keys are discarded.

## React Host Fallback

- **Fields**: mount path, bootstrap URL, config URL, asset manifest availability, CSP headers, non-Jinja response header.
- **Rules**: Fallback HTML is static string assembly and never uses a template provider.

## Dependency Metadata

- **Fields**: project dependency list, lockfile package list, direct requirement entries.
- **Rules**: `jinja2` must be absent from project dependencies and lock metadata after refresh.

## Rollback Plan

- **Fields**: plan id, status, owner label, steps, verification steps, audit reference.
- **Rules**: Rollback is redeploying the previous release and verifying React/static asset health; no feature flag re-enables templates in this release.
