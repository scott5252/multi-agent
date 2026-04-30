# Skill Registry

The skill registry adds a governed lifecycle for declarative agent skills.
Platform administrators create packages, validate manifests, publish immutable
versions, and grant tenant availability. Tenant administrators install exact
versions, configure credential references, run smoke tests, and expose only
ready installations to existing model-skill binding policy.

## Platform Flow

1. Open `/admin/skill-registry/ui/packages`.
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

1. Open `/admin/skill-registry/ui/installations` in tenant scope.
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
- UI: `/admin/skill-registry/ui/packages` and
  `/admin/skill-registry/ui/installations`.
- Runtime adapter: `multi_agent_platform.runtime.skill_registry`.
- Policy adapter:
  `multi_agent_platform.admin.skill_registry.eligibility`.
