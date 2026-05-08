# Research: Membership And Access React Live Data

## Decision: Use existing membership services and repositories as the live source of truth

**Rationale**: `MembershipRepository` already owns persisted principal identities, user invitations, tenant memberships, role grants, access decisions, and membership audit records. `MembershipAdministrationService` already enforces platform versus tenant authority, role assignment guardrails, invitation replay/idempotency, membership status transitions, role grant mutation, principal status mutation, and audit writes. The React builder should compose these durable records into backend-owned JSON instead of recreating fixed demo rows.

**Alternatives considered**: Keeping deterministic QA034 projection data behind a new adapter was rejected because it would still invent production rows. Reading database models directly from routes was rejected because it duplicates service authorization and redaction logic.

## Decision: Resolve platform and tenant scope in the backend shell and membership access scope

**Rationale**: The React shell already resolves active scope and available scope options from the authenticated principal and tenant query. Membership live data should translate that shell scope into `MembershipAccessScope` before querying or mutating data. This keeps Auth0-shaped and local-principal behavior aligned and prevents browser state from expanding scope.

**Alternatives considered**: Letting the frontend filter or select broader scope was rejected because it can leak unauthorized tenant labels or cross-tenant identifiers. Adding a new scope resolver was rejected unless existing shell resolution cannot provide the necessary tenant/platform distinction.

## Decision: Render only backend-redacted identity and audit summaries

**Rationale**: Membership data includes full emails, external subjects, IdP claims, actor identifiers, tenant labels, and audit metadata. Existing redaction helpers such as `mask_email`, `mask_identifier`, `safe_membership_text`, and `sanitize_metadata` should be used before any schema response is created. Schema validators should continue rejecting unsafe text so route tests catch regressions.

**Alternatives considered**: Browser-side masking was rejected because raw values would still cross the JSON boundary. Rendering raw audit metadata for platform admins was rejected because screenshots and QA artifacts must remain redaction-safe.

## Decision: Add explicit live provenance and truthful empty states

**Rationale**: The live-data roadmap requires operators and QA reviewers to distinguish persisted rows from empty/denied/unavailable states. Membership responses should include source/provenance and empty-state metadata for directory, invitations, grants, status actions, access history, and audit timeline without inventing rows.

**Alternatives considered**: Inferring empty state from empty arrays alone was rejected because it does not explain whether data is absent, denied, or unavailable. Keeping only summary counts was rejected because individual panels need per-section empty messaging.

## Decision: Validate one durable invitation action through Playwright

**Rationale**: Creating or replaying an invitation is a safe visible membership action that exercises idempotency, masking, requested roles, audit writes, next-request effect text, frontend mutation handling, and repository persistence without changing external identity providers. It can be seeded and verified in the qa054 database.

**Alternatives considered**: Principal linking was rejected as the primary Playwright action because platform-only authority and Auth0-shaped subject semantics are more sensitive. Role grant revocation and membership removal were rejected as primary actions because they can accidentally remove QA access if seeds drift.

## Decision: Keep fixed QA034 markers only in test and historical artifacts

**Rationale**: Production membership builders and routes must not return fixed QA034 IDs, users, invitations, role grants, access decisions, or audits. Test fixtures, historical specs, and QA docs may still contain old labels when they are not imported by production code. Scanner guardrails should enforce this boundary.

**Alternatives considered**: Deleting all QA034 text was rejected because it would remove useful historical and test-only context outside the production surface.
