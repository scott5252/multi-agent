# Research: Workflow Registry Full React Parity And Jinja Removal

## Decision: `/admin/app/workflows` Is The Canonical Workflow Browser Surface

**Rationale**: Spec 030 already established the React workflow builder at `/admin/app/workflows`, and Spec 039 moved the admin host to non-Jinja rendering. Keeping one canonical React path avoids parallel workflow experiences and gives old links a stable redirect target.

**Alternatives considered**:

- Keep `/admin/workflows/ui` as a browser page until Spec 047. Rejected because Spec 040 owns workflow browser removal and would leave workflow templates active.
- Add a second React workflow path under `/admin/workflows/react`. Rejected because it increases direct-link and saved-filter ambiguity.

## Decision: Legacy Workflow URLs Redirect When State Preservation Is Safe

**Rationale**: Workflow URLs often carry tenant scope, ids, filters, saved-filter intent, validation anchors, revision ids, and publish-gate context. Redirecting preserves support/bookmark behavior when parameters map unambiguously to React routes. Unsafe, missing, or unauthorized context must fail closed with a non-Jinja problem or gone response.

**Alternatives considered**:

- Return gone for all old workflow URLs. Rejected because it breaks safe direct links unnecessarily.
- Preserve all query parameters blindly. Rejected because it risks open redirects, tenant leakage, or stale conflict ambiguity.

## Decision: Extend The Existing Workflow Builder Envelope

**Rationale**: The current React builder already has draft, graph, validation, publish readiness, revisions, reference picker, mutation result, and JSON inspector concepts. Full parity needs list, create, published detail, sharing, old route mappings, and direct-link states layered onto that contract, not a new workflow persistence model.

**Alternatives considered**:

- Build separate list/detail contracts from scratch. Rejected because it duplicates workflow registry service decisions.
- Render raw workflow registry records directly in React. Rejected because redaction and safe-summary rules require backend-owned presentation contracts.

## Decision: Legacy Form Posts Become JSON Or Redirect Compatibility Handlers

**Rationale**: Workflow create/save/validate/publish/copy/restore actions already have JSON APIs and React mutation patterns. Legacy form endpoints must not render templates after completion; they either redirect to React with safe state or return backend-owned JSON/problem responses for non-browser clients.

**Alternatives considered**:

- Keep old form posts until global Jinja removal. Rejected because form actions are workflow-owned browser behavior.
- Convert all form posts to browser redirects only. Rejected because validation, stale conflict, and publish readiness need structured responses.

## Decision: Graph Accessibility Requires Visual And List Coverage

**Rationale**: Deletion-grade parity includes users who cannot operate the graph visually. The React workflow graph must keep keyboard-readable lists for nodes, edges, validation findings, and publish blockers, with tests and Playwright evidence.

**Alternatives considered**:

- Validate only visual graph screenshot parity. Rejected because it misses keyboard and screen-reader workflows.
- Remove graph view until later. Rejected because graph preview is explicitly in scope for workflow parity.

## Decision: Delete Workflow Static Assets Only After Scanner Proof

**Rationale**: `workflow_studio.js` and `workflow_studio.css` are workflow-named assets, but deletion must wait until route tests and scanner/import checks show no remaining workflow or non-workflow references. Retained assets require blocker evidence.

**Alternatives considered**:

- Delete assets as soon as React components exist. Rejected because old templates and docs may still reference them.
- Retain assets through Spec 047. Rejected if Spec 040 proves they are workflow-only and unused, because bounded deletion should happen in the owning spec.
