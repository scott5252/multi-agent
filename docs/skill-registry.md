# Skill Registry

The skill registry adds a governed lifecycle for declarative agent skills.
Platform administrators create packages, validate manifests, publish immutable
versions, and grant tenant availability. Tenant administrators install exact
versions, configure credential references, run smoke tests, and expose only
ready installations to existing model-skill binding policy.

## Platform Flow

1. Open `/admin/app/skills/packages`.
2. Create a package with a stable slug, owner, description, and safe summary.
3. Validate a manifest that references approved tool or MCP integrations only.
4. Publish the version after validation returns no blocking findings.
5. Grant availability to selected tenants or all tenants.
6. Review validation findings, artifact digests, tenant grants, quarantine
   state, and safe audit events from the package and version pages.

Published package versions are immutable. Any change to manifest content,
documentation, fixtures, compatibility, permissions, or entrypoint references
requires a new semantic version.

## Tenant Flow

1. Open `/admin/app/skills/installations` in tenant scope.
2. Install an authorized package version.
3. Configure required credentials using existing secret references or
   delegated credential links.
4. Run declared smoke tests.
5. Promote readiness only after credentials, compatibility, permissions, smoke
   tests, and quarantine checks pass.
6. Preview binding eligibility before connecting the installation to an agent
   profile or workflow role.

Installations pin package slug, semantic version, installation version,
manifest digest, artifact digest, and readiness evidence. Upgrades create new
installation versions; existing bindings never float automatically.

## Security Rules

- Raw package secrets, credential values, provider tokens, unsafe docs,
  fixtures, and cross-tenant data are not stored or rendered.
- Manifest entrypoints are limited to `approved_tool_ref` and
  `approved_mcp_ref`.
- Stale readiness or credential updates require the current revision token and
  are rejected with safe audit evidence.
- Quarantine blocks new installs, readiness promotion, new bindings, workflow
  publish validation, and runtime use until resolved.

## Operator Surfaces

- JSON API: `/admin/skill-registry/packages`,
  `/admin/skill-registry/packages/{slug}/versions`,
  `/admin/skill-registry/installations`, and installation eligibility routes.
- React UI: `/admin/app/skills/packages` and
  `/admin/app/skills/installations`.
- Legacy browser URLs under `/admin/skill-registry/ui/*` are authenticated
  redirects to the React skill workspace and no longer render skill registry
  Jinja templates.
- Runtime adapter: `multi_agent_platform.runtime.skill_registry`.
- Policy adapter:
  `multi_agent_platform.admin.skill_registry.eligibility`.

## Runtime Tool Execution

Spec 021 adds a governed SkillExecutionGateway for read-only Daily Briefing
tools. Runtime graph role nodes use the gateway instead of calling connector
adapters directly. The gateway checks installed package/version metadata, tool
allow policy, outbound domains, side-effect defaults, execution mode, tenant
credential metadata, and redaction before any adapter is invoked.

First-party mock adapters are available for:

- `google_calendar.events.read`
- `gmail.messages.read`
- `news.search`
- `weather.forecast.read`
- `commute.lookup`

Local QA uses deterministic mock fixtures and safe delegated credential
metadata. Live probes are staging-only and require an explicit live-probe mode,
non-local environment, matching tenant credential metadata, and outbound
allowlist policy. Raw external provider payloads and raw secret values are not
stored inline; diagnostics show only redacted request and response summaries.

Operators can review connector readiness at `/admin/app/skills/diagnostics`.
The legacy `/admin/skill-execution/ui/diagnostics` URL redirects to the React
diagnostics workspace. The JSON diagnostics endpoints are
`/admin/skill-execution/api/diagnostics` and
`/admin/skill-execution/api/diagnostics/run`.
