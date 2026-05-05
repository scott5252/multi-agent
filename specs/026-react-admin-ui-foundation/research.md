# Research: React Admin UI Foundation

## Decision: Mount Path And Routing

Use `/admin/app` as the initial React app mount path and Vite SPA routing for
Spec 026.

**Rationale**: The path is separate from existing Jinja admin routes, easy to
authorize through a dedicated FastAPI router, and aligns with the roadmap's
additive migration model.

**Alternatives considered**:
- Replace `/admin`: rejected because it would couple the foundation to domain
  parity before later specs prove migration safety.
- Per-domain React mount paths now: rejected because Spec 026 must not migrate
  domain pages.

## Decision: Jinja Fallback Strategy

Keep existing Jinja routes direct and authorized, and render fallback links
from backend-owned navigation metadata.

**Rationale**: Current admin flows stay stable, every fallback still passes
through existing policy checks, and future React route enablement can remain
feature-flagged.

**Alternatives considered**:
- Redirect all admin traffic through React: rejected because it changes the
  production operator path too early.
- Hard-code browser fallback links: rejected because the browser must not
  duplicate authorization or navigation policy.

## Decision: Session And Action Protection

Reuse the existing authenticated request context for shell/bootstrap requests,
avoid browser-stored provider credentials, and introduce backend-issued
CSRF/action token fields for protected React actions.

**Rationale**: The backend remains the source of truth for Auth0 and
local-principal behavior while the browser receives only scoped, purpose-bound
action protection.

**Alternatives considered**:
- Store identity provider tokens in React state: rejected for secret hygiene.
- Trust client-side role flags: rejected because authorization must fail
  closed server-side.

## Decision: Contract And Type Generation

Define Pydantic response schemas for React admin bootstrap/config/manifest
data, expose the contract through FastAPI/OpenAPI, and generate TypeScript
types into `frontend/admin/src/api/generated`.

**Rationale**: This matches the repository's Pydantic contract style and keeps
browser models synchronized with backend schemas.

**Alternatives considered**:
- Hand-maintained TypeScript interfaces only: rejected because drift would be
  hard to detect.
- Generate backend schemas from frontend types: rejected because backend
  services and policy helpers remain authoritative.

## Decision: Package Manager And Node Policy

Use npm with `package-lock.json` for the first frontend workspace and require
Node.js `>=20.19.0 <26` for the Vite toolchain.

**Rationale**: The repository has no existing Node package manager lockfile,
and npm keeps the foundation small and widely reproducible. The Node policy
matches the roadmap's Vite compatibility requirement while avoiding untested
future major versions in CI.

**Alternatives considered**:
- pnpm workspace: rejected for Spec 026 because no existing monorepo frontend
  workspace needs shared package management yet.
- Yarn: rejected because it adds another package manager without a local
  precedent.

## Decision: Asset Serving

Use the Vite dev server only for local development through a documented proxy,
and serve production-like builds from FastAPI under `/admin/static/react`.

**Rationale**: Production admin requests stay behind the existing FastAPI app,
while developers get fast local frontend iteration.

**Alternatives considered**:
- Run Vite in production: rejected because it introduces a second production
  serving path and unclear auth/static controls.
- Inline all assets in Jinja: rejected because future React specs need normal
  build artifacts and cacheable assets.

## Decision: Feature Flag Rollout

Add backend-controlled flags for React foundation availability and future
domain route enablement.

**Rationale**: The foundation can be switched on for QA while domain pages
remain disabled until their owning specs complete.

**Alternatives considered**:
- Browser-only flags: rejected because the backend must decide route access and
  navigation visibility.
- No flags until later: rejected because domain route guardrails are part of
  the foundation acceptance criteria.
