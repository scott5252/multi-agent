# Model Provider Gateway

Spec 011 adds platform-admin-managed provider connections and a shared
`ModelGateway` path for model calls. The admin UI lives at
`/admin/model-providers` inside the shared admin shell.

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

## Review Checks

Use the Spec 011 QA guide and UI guide for copy/paste verification:

- `specs/011-model-provider-gateway/qa011.md`
- `specs/011-model-provider-gateway/QA011_UI.MD`
- `specs/011-model-provider-gateway/testing-instructions.md`
