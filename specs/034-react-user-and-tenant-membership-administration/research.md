# Research: React User And Tenant Membership Administration

## Decision: Reuse Spec 018 Membership Domain Services

**Rationale**: Existing membership services already enforce tenant scope,
idempotent invitations, role eligibility, principal status, audit records,
masked email handling, and next-request grant behavior. React should render
safe projections and submit actions to backend-owned mutation routes.

**Alternatives considered**: Reimplement role eligibility in React. Rejected
because browser-side authorization would duplicate security rules and drift
from Auth0/local-principal behavior.

## Decision: Backend-Owned Directory Projection

**Rationale**: The directory needs display names, masked emails, safe subject
suffixes, tenant labels, role summaries, status, last access, and allowed
actions. A backend projection can bound list sizes, preserve tenant isolation,
and omit unsafe identifiers.

**Alternatives considered**: Fetch raw users, grants, invitations, and history
separately and join in React. Rejected because it increases leakage risk and
pushes domain rules into the browser.

## Decision: Guided Invite And Role Grant Workflows

**Rationale**: Non-technical administrators need clear forms with eligible role
choices, tenant scope, confirmation copy, field errors, idempotency replay,
stale recovery, and next-request effect summaries. Backend form metadata keeps
role choices and confirmation requirements authoritative.

**Alternatives considered**: Generic JSON editor or raw table actions. Rejected
because it makes raw identifiers primary and does not satisfy safe admin UX.

## Decision: Masked Identity By Default, Authorized Detail On Demand

**Rationale**: Email and external subject identifiers can be sensitive in
screenshots and audit evidence. The primary UI should show masked email and
safe subject suffixes. Copyable raw identifiers are shown only when the backend
marks them safe and authorized.

**Alternatives considered**: Always show full email addresses for admin
convenience. Rejected because QA artifacts and screenshots must be shareable
without cleanup.

## Decision: Confirmation For Access-Changing Actions

**Rationale**: Suspend, reactivate, remove membership, revoke grant, and
principal-link overwrite can immediately affect access. Explicit confirmation
reduces accidental destructive changes and produces clearer audit evidence.

**Alternatives considered**: Single-click actions with undo. Rejected because
access revocation and suspension must be durable, auditable decisions.

## Decision: Bounded Access History Timeline

**Rationale**: Access history is valuable for explainability but can grow
unbounded. The React route should render a bounded recent timeline with safe
filters and links to authorized deeper views.

**Alternatives considered**: Load all access decisions for a principal. Rejected
for performance and leakage risk.

## Decision: Dual Auth Validation Is Mandatory

**Rationale**: Membership administration is security-sensitive. Route tests
must prove Auth0-shaped principal claims and local-principal catalog behavior,
and Playwright must prove local-login browser workflows.

**Alternatives considered**: Validate only local-principal mode. Rejected
because production membership behavior depends on Auth0-backed identities.
