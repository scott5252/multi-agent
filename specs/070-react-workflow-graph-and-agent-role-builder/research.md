# Research: React Workflow Graph And Agent Role Builder

## Decision: Persist Editor Changes Through The Spec 069 Full-Document Save Contract

**Rationale**: Spec 069 added typed full-document save, idempotency, stale conflict, validation mapping, and editor state return values. Reusing that contract keeps authorization, tenant scope, validation, audit, redaction, and revision behavior backend-owned while allowing the browser to compose section changes locally.

**Alternatives considered**:

- Add per-section patch endpoints. Rejected for Spec 070 because they would duplicate revision/idempotency/validation semantics before the UI proves the full section model.
- Store graph editor changes in local browser state only. Rejected because it violates durable source-of-truth requirements and would not survive reload.

## Decision: Use Existing `@xyflow/react` For Canvas Rendering

**Rationale**: The admin frontend already uses `@xyflow/react` in workflow graph and agent graph panels, and the dependency is already present in `frontend/admin/package.json`. Reusing it avoids a package policy change and keeps visual behavior consistent.

**Alternatives considered**:

- Add a new graph library. Rejected because there is no need for a new dependency.
- Draw a custom SVG graph editor. Rejected because existing graph panels and tests already cover the current canvas library.

## Decision: Required Editing Surface Is Forms And Keyboard-Readable Lists

**Rationale**: The roadmap requires browser controls and keyboard alternatives. Form/list editors are accessible, testable, and deterministic. A direct drag-and-drop canvas can be layered later, but it must not be the only editing path.

**Alternatives considered**:

- Direct manipulation canvas as primary editor. Deferred because it increases accessibility and persistence risk.
- Raw JSON editor for advanced users. Rejected because the roadmap explicitly requires custom workflow setup without raw JSON editing.

## Decision: Keep Prompt/Profile Create And Publish Flows Out Of Scope

**Rationale**: Spec 071 owns prompt/profile creation, publishing, activation, and per-agent binding workflows. Spec 070 should only maintain safe role reference placeholders and summaries that future Spec 071 controls can populate.

**Alternatives considered**:

- Build prompt/profile editing in this spec. Rejected because it would combine two large user journeys and blur validation responsibility.

## Decision: Dependency-Aware Delete Behavior Uses Validation Warnings, Not Silent Cascades

**Rationale**: Roles, contracts, nodes, edges, joins, approvals, and subworkflows reference each other. Silent cascade deletion could remove meaningful workflow behavior without clear user intent. Spec 070 should warn or block when dependent references exist and let users remove dependencies explicitly.

**Alternatives considered**:

- Cascade delete dependent graph entries. Rejected as too destructive for a first browser editor slice.
- Allow deletion and rely on later validation. Rejected because it creates confusing dirty states when dependencies are visible.

## Decision: Playwright Must Exercise A Real Authoring Journey

**Rationale**: Specs 070 through 073 must strengthen the generated smoke flow. Spec 070 should create or open a draft, add at least three roles, add graph nodes and edges, add a join, save, reload, and capture desktop/mobile screenshots that prove canvas and list alternatives render.

**Alternatives considered**:

- Keep the generated smoke route only. Rejected by the workflow setup autopilot validation contract for Specs 070 through 073.
