# PR Review Notes: Model Skill Routing

- Deterministic precedence is step, agent, workflow, tenant default for models.
- Prompt provenance is independent and excludes tenant-global prompt fallback.
- Version pinning stores accepted run candidates and first-use decisions before side effects.
- Rollback reactivates immutable prior versions and does not mutate history.
- Skill binding enforcement and tool policies deny by default.
- Outbound egress checks normalize hosts and reject embedded credentials.
- Credentials and secret references persist metadata only; raw secret hygiene is required in audits, logs, traces, docs, and tests.
- Audit completeness includes create, activate, preview denial, validation failure, authorization failure, rollback, migration, and runtime allow or deny decisions.
- Authorization must fail closed across tenants for admin views, APIs, runtime resolution, provenance, and history.
- Known risks: runtime integration currently needs end-to-end worker wiring for full first-use enforcement and migration compatibility checks.

