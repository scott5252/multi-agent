# Research: Governance Full React Parity And Jinja Removal

## Decision: Extend Existing React Governance Contracts

**Rationale**: Spec 031 already established backend-owned governance schemas, deterministic service builders, React components, and route tests. Extending those contracts minimizes blast radius and keeps authorization, tenant scope, redaction, provider safety, prompt safety, and provenance decisions on the backend.

**Alternatives considered**:

- Build new governance JSON contracts from scratch: rejected because it would duplicate existing services and increase drift.
- Keep Jinja pages for missing flows: rejected because Spec 041's goal is deletion-grade React parity.

## Decision: Use Stable React Governance Child Routes For Direct Links

**Rationale**: Old URLs for provider detail/edit/catalog/test results, prompt detail/edit/history/preview, profile detail/edit/history/resolve, and model-skill config history/provenance need bookmark recovery. Stable child routes under `/admin/app/governance` let browser refreshes and redirects land on one non-Jinja host while React fetches backend-owned state.

**Alternatives considered**:

- Redirect every old governance URL to only `/admin/app/governance`: rejected because reviewers would lose direct-link context.
- Keep old pages as retained fallbacks: rejected for governance-owned pages where parity evidence is available.

## Decision: Convert Old Browser GET Routes Before Template Deletion

**Rationale**: Model provider, prompt, agent profile, and model-skill config routers currently include TemplateResponse-backed browser views. Those GET routes should become redirects or safe problem responses after React parity is proven. JSON/API routes used by React should stay intact.

**Alternatives considered**:

- Delete routers wholesale: rejected because existing API routes and auth policies may still be used.
- Remove global Jinja templates/providers now: rejected because later specs still own other Jinja domains.

## Decision: Preserve Backend-Owned Mutation Authorization

**Rationale**: Provider create/edit/catalog sync/probe/test, credential-reference changes, prompt/profile save, prompt preview, profile resolution, routing preview, and direct-call guardrail evidence all depend on existing authorization, audit, redaction, and service behavior. React must render action metadata and safe mutation results rather than deciding permissions.

**Alternatives considered**:

- Hide controls only in React: rejected because browser-only authorization is unsafe.
- Permit tenant-admin provider mutations for parity: rejected because it changes established role boundaries.

## Decision: Use Deterministic Mocked-Safe Probes And Previews In Validation

**Rationale**: Local and CI validation must exercise provider/probe/preview/routing/resolution/provenance behavior without real Auth0, provider, Telegram, credential, connector, external tool, or direct SDK calls.

**Alternatives considered**:

- Run live provider probes in QA: rejected due credential and external side-effect risk.
- Skip probe/preview validation: rejected because those flows are core governance parity requirements.

## Decision: Delete Governance-Owned Templates Only With Scanner And Route Evidence

**Rationale**: Templates under `model_providers`, `prompts`, `agent_profiles`, and `model_skill_config` are in active scope. They can be deleted only after redirects, React contracts, route tests, redaction checks, QA docs, and Playwright prove parity. Shared shell templates and other domain templates remain for later specs.

**Alternatives considered**:

- Delete all Jinja templates now: rejected because Specs 042-047 still own other domains and global infrastructure.
- Retain governance templates with a broad blocker: rejected unless a specific route/helper lacks parity evidence.
