# Research: Model Provider Gateway

## Decision: Use provider adapters over `httpx.AsyncClient`

**Rationale**: OpenAI and local OpenAI-compatible endpoints can share one
request/response normalization path, timeout handling, and mocked transport
strategy. Avoiding provider SDK calls keeps secret handling, retries, breakers,
traces, and tests under the platform's existing dependency and observability
model.

**Alternatives considered**: Provider SDKs were rejected because direct SDK use
would fragment retries, logging, and test behavior. A purely LangChain-level
adapter was rejected for this feature because the gateway must capture
connection health, catalog governance, usage metadata, and safe audit evidence
before framework-specific execution.

## Decision: Treat local providers as OpenAI-compatible chat completions

**Rationale**: The feature clarification chose OpenAI-compatible local
providers. One contract supports safe probes, runtime calls, mocked provider
tests, and future endpoint implementations without inventing an adapter shape
for every local runtime.

**Alternatives considered**: Adapter-specific local APIs were deferred because
they would require per-provider schemas, probe behavior, and usage extraction.
Generic passthrough HTTP was rejected because it could bypass secret hygiene
and response redaction.

## Decision: Enforce an administrator-managed local endpoint allowlist

**Rationale**: Local model endpoints create outbound access risk. A configured
allowlist of schemes, hosts, ports, and CIDRs lets platform administrators
control permitted local infrastructure while failing closed before any network
probe when the URL is outside policy.

**Alternatives considered**: Per-tenant allowlists were rejected for initial
scope because provider connections are platform-admin-managed. DNS-only
matching was rejected because CIDR and explicit port controls are required for
private network safety.

## Decision: Store only secret references and resolve at use time

**Rationale**: Existing secret providers already own raw credential material.
Provider connection records, catalog entries, logs, traces, and audit summaries
store only reference ids and safe metadata; tests and runtime calls resolve
references in memory immediately before adapter invocation.

**Alternatives considered**: Copying API keys into encrypted connection rows
was rejected because it duplicates secret storage. Resolving and caching secret
values in the database was rejected because it violates secret hygiene and
rotation expectations.

## Decision: Publish managed entries into the existing model_skill_config catalog

**Rationale**: Model routing already resolves model provider catalog entries
and pins runtime decisions. Extending those rows with gateway governance fields
avoids a parallel catalog and lets existing routing, provenance, and runtime
pinning continue to work.

**Alternatives considered**: A separate gateway catalog was rejected because it
would create two sources of routing truth. Replacing model_skill_config
resolution was rejected because it would widen scope and risk existing routing
behavior.

## Decision: Routing selects only healthy active tenant-visible entries

**Rationale**: The spec clarification requires healthy-only selection. Health
is derived from active state and latest relevant test evidence, so the runtime
fails closed when health, visibility, credentials, or catalog governance cannot
be verified.

**Alternatives considered**: Allowing degraded entries was rejected by
clarification. Allowing untested entries during rollout was rejected because it
would weaken provider governance and review evidence.

## Decision: Normalize provider errors into stable categories

**Rationale**: Administrators, audits, retry classifiers, and breakers need
safe, stable failure categories. The gateway maps authorization failure,
invalid model, timeout, rate limit, provider unavailable, malformed response,
policy or visibility denial, secret resolution failure, and unknown provider
failure without storing raw provider bodies.

**Alternatives considered**: Persisting raw provider errors was rejected for
secret and prompt leakage risk. Provider-specific error enums were rejected
because routing and operations need provider-neutral categories.

## Decision: Use safe deterministic probes

**Rationale**: Probes must validate credentials, endpoint reachability, model
id, response shape, timeout, and usage extraction without using tenant prompts.
The stored result keeps timestamp, actor/source, latency, tested model, outcome
category, and sanitized diagnostics only.

**Alternatives considered**: Listing models was rejected as the sole probe
because some local endpoints may not implement model listing. Using customer
workflow prompts was rejected because test evidence must not persist protected
content.

## Decision: Reuse existing reliability retries and breakers

**Rationale**: The platform already has retry classifiers and circuit breaker
state. Gateway calls supply safe retry and breaker inputs with stable scope
names, preserving operational behavior and dashboard consistency.

**Alternatives considered**: Implementing independent gateway retries was
rejected because it would duplicate policy and make incident review harder.
Provider SDK retries were rejected because they are harder to audit and align
with tenant fairness controls.

## Decision: Add shared admin shell pages for full provider lifecycle

**Rationale**: The user explicitly requires Web UI updates, and the existing
admin console shell now owns shared navigation, scope selection, flash states,
and saved filters. Provider list, create/edit, detail, tests, and catalog pages
make connection health and tenant visibility discoverable without direct API
use.

**Alternatives considered**: API-only delivery was rejected because it fails
the Web UI requirement and the success criterion that admins locate health,
last test, visibility, and catalog state without assistance.

## Decision: Measure gateway overhead with mocked providers

**Rationale**: Provider network latency is outside platform control. Mocked
transports isolate gateway overhead for validation, redaction, catalog lookup,
retry/breaker checks, usage extraction, trace capture, and audit summary
construction.

**Alternatives considered**: Measuring only end-to-end OpenAI calls was
rejected because external latency would make the platform overhead target
unstable. Micro-benchmarking individual functions was rejected because the
contract is end-to-end gateway wrapper overhead.
