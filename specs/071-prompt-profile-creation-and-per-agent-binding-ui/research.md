# Research: Prompt Profile Creation And Per-Agent Binding UI

## Decision: Reuse Existing Prompt And Profile Domains

**Decision**: Spec 071 will reuse `admin_prompts.py`, `admin_agent_profiles.py`, prompt repository/service, agent profile repository/service, and generated React contract output instead of creating a second prompt/profile storage domain.

**Rationale**: The existing domains already own prompt lineage/draft/version state, runtime profile draft/version state, validation, publication, activation, tenant/platform grants, stale revision behavior, and redaction-safe summaries. Reusing them preserves durable versioning and avoids divergent publish-readiness logic.

**Alternatives considered**: A workflow-builder-only prompt/profile store was rejected because it would duplicate source-of-truth state and break version-pinned runtime execution.

## Decision: Workflow Role Bindings Use Full Document Save

**Decision**: Per-agent binding controls will write `prompt_profile_references`, `roles[].profile_reference_key`, and `roles[].prompt_reference_keys` through the Spec 069 workflow document save contract.

**Rationale**: Spec 069 already provides revision tokens, idempotency keys, stale recovery, validation mapping, and audit-safe mutation summaries for workflow document edits.

**Alternatives considered**: New narrow workflow binding endpoints were rejected for Spec 071 because they would need to duplicate stale/idempotency behavior already implemented in the full document save route.

## Decision: Safe Catalogs Instead Of Raw Prompt/Profile Payloads

**Decision**: Workflow setup uses safe prompt/profile catalog items and binding summaries. Raw prompt template content is fetched or edited only inside authorized prompt edit forms and is not copied into workflow summaries, graph panels, screenshots, JSON inspectors, audit summaries, docs, logs, or exports.

**Rationale**: The workflow setup UI must help users bind prompts/profiles without turning the whole workflow builder into a raw prompt display surface.

**Alternatives considered**: Showing raw prompt previews in the role binding matrix was rejected because it would violate the raw prompt exposure boundary.

## Decision: Deterministic Fake/Local Readiness In QA

**Decision**: QA data will seed tenant-scoped prompt/profile records with deterministic fake secret references and local/provider readiness summaries. No real provider, credential, connector, model, Telegram, or outbound calls are allowed.

**Rationale**: The roadmap requires deterministic local-principal QA while still exercising backend authorization, tenancy, validation, readiness, save/reload, and redaction behavior.

**Alternatives considered**: Live provider probes were rejected because Spec 071 does not explicitly approve external side effects.

## Decision: Keep Test Evidence Out Of Scope

**Decision**: Spec 071 may display missing test-evidence blockers but will not create test suites, cases, runs, or publish-gate evidence. That scope remains Spec 072.

**Rationale**: Prompt/profile binding must be independently complete before custom workflow test evidence setup. Separating the slices keeps implementation reviewable and validation focused.

**Alternatives considered**: Building prompt/profile and test evidence in one pass was rejected because it would blur ownership with Spec 072 and increase validation blast radius.
