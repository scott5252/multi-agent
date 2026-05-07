# Model Provider Gateway

Spec 011 adds platform-admin-managed provider connections and a shared
`ModelGateway` path for model calls. The admin UI lives at
`/admin/app/governance/providers` inside the React admin shell; old
`/admin/model-providers` browser routes redirect there.

## Admin Workflow

Platform administrators can create OpenAI and local OpenAI-compatible
connections with:

- Provider type and display name.
- Safe base URL metadata for local providers.
- One or more model ids.
- Timeout policy for probes and runtime calls.
- Tenant visibility as platform default or explicit tenant allowlist.
- Credential secret reference ids.
- Active or inactive state.

Tenant-scoped users can view only connections visible to their tenant. Mutation,
activation, deactivation, testing, and catalog synchronization require platform
administrator authority.

## Local Provider Safety

Local OpenAI-compatible providers must pass the administrator allowlist before
probe or runtime use. The allowlist covers schemes, hosts, ports, and CIDR
ranges. URLs with userinfo or secret-like query parameters are rejected before a
network call is attempted.

## Safe Probes And Health

Connection tests use a non-customer safe probe. Results store timestamp,
actor/source, latency, tested model, outcome, normalized reason, and safe
diagnostics. Raw prompts, completions, provider response bodies, API keys,
tokens, Authorization headers, and endpoint secrets are not persisted.

Credential secret reference ids are resolved through the configured secret
provider only at probe time. OpenAI probes require a resolvable reference and
fail closed with `secret_reference_invalid` before any provider call when the
reference is missing or invalid. Local OpenAI-compatible probes may remain
no-auth only for allowlisted local endpoints.

Health states are derived from active state and latest probe evidence:
`disabled`, `untested`, `healthy`, `degraded`, `failing`, and `unavailable`.
Routing may select only healthy, active, tenant-visible, gateway-governed
entries.

## Catalog Publication

Catalog sync records durable evidence for each configured model and visibility
scope. Healthy active connections produce selectable gateway-governed catalog
entries. Inactive or unhealthy connections are marked unavailable instead of
deleting history. Tenant-scope model collisions are blocked at publication time.

## Runtime Gateway

Runtime and test bench model attempts go through `ModelGateway`. Each attempt
records selected connection/model context, latency, outcome, normalized error,
usage availability, retry/breaker summaries, and a safe audit summary. The
gateway response keeps provider content in memory only and does not persist raw
prompts or completions.

`ModelGateway` resolves provider credentials at call time from the connection's
ordered safe reference list. Resolved values are passed only into the adapter
request and are never written to gateway attempts, operations, physical
attempts, usage records, or audit summaries.

## Review Checks

Use the Spec 011 QA guide and UI guide for copy/paste verification:

- `specs/011-model-provider-gateway/qa011.md`
- `specs/011-model-provider-gateway/QA011_UI.MD`
- `specs/011-model-provider-gateway/testing-instructions.md`
- `specs/025-live-model-credential-resolution-for-gateway-calls/qa025.md`
- `specs/025-live-model-credential-resolution-for-gateway-calls/qa025_ui.md`
- `specs/025-live-model-credential-resolution-for-gateway-calls/testing-instructions.md`
