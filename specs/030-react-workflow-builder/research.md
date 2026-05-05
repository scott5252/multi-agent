# Research: React Workflow Builder

## Decision 1: Use A Proven Graph Library For Visual Graph Review

**Decision**: Plan implementation around `@xyflow/react` for the visual workflow graph if dependency addition is accepted during implementation.

**Rationale**: The current React Flow site positions the library for node-based editors and interactive diagrams, and its official accessibility page documents keyboard focus, selection, arrow-key movement, auto-pan on node focus, ARIA descriptions, and WCAG-oriented guidance. This matches the workflow builder's need for a graph canvas while still requiring a non-canvas list alternative.

**Sources**:

- [React Flow homepage](https://reactflow.dev/)
- [React Flow accessibility documentation](https://reactflow.dev/learn/advanced-use/accessibility)
- [React Flow quick start](https://reactflow.dev/learn/getting-started/installation-and-requirements)

**Alternatives Considered**:

- Hand-rolled SVG/canvas graph: rejected because workflow editors have established interaction, accessibility, panning, zooming, edge, and node-state concerns.
- Static graph preview only: rejected because the feature requires graph-oriented editing/review, though backend semantics remain authoritative.

## Decision 2: Backend Validation Owns Execution Semantics

**Decision**: React graph edits produce semantic document save requests. Backend validation determines valid nodes, edges, fan-out, join policies, approval gates, reusable subworkflow references, and publish readiness.

**Rationale**: Specs 003, 013, 020, and 024 already define workflow registry, builder/publish gates, graph execution, and required test evidence. Duplicating these rules in the browser would risk drift and tenant/security mistakes.

**Alternatives Considered**:

- Browser-side graph validation: rejected except for harmless UI hints.
- Saving graph positions as authoritative execution shape: rejected; layout is visual and non-authoritative.

## Decision 3: Explicit Saves Instead Of Autosave

**Decision**: Draft changes remain dirty in the browser until the admin submits an explicit backend save.

**Rationale**: Workflow drafts affect publishable runtime behavior. Explicit save creates cleaner revision history, safer stale-conflict handling, and clearer audit evidence. This follows the clarify default.

**Alternatives Considered**:

- Autosave every field change: rejected because it creates noisy revisions and harder audit review.
- Local-only draft cache: rejected for QA because it would not exercise backend revision and stale-conflict contracts.

## Decision 4: Read-Only Collapsed JSON Inspector

**Decision**: Provide a collapsed advanced JSON inspector that renders backend-redacted read-only content.

**Rationale**: Non-technical admins should use guided controls first. Advanced review is still useful for support and platform operators, but raw document editing in the browser would bypass safe form constraints and make redaction harder to prove.

**Alternatives Considered**:

- Editable JSON mode: rejected as primary or fallback authoring for Spec 030.
- No JSON visibility: rejected because reviewer/support workflows sometimes need structured inspection.

## Decision 5: Required Evidence Blocks Publish

**Decision**: Publish readiness must include repository-backed required test-suite evidence from Spec 024, validation freshness, reference readiness, revision freshness, and confirmation requirements.

**Rationale**: Workflow publish actions create immutable runtime bundles. Missing or stale test evidence must be visible in the publish gate and block publish.

**Alternatives Considered**:

- Treat evidence as advisory: rejected because Spec 024 makes required evidence part of publish gates.
- Client-side evidence override: rejected; backend gate owns decisions.

## Decision 6: Dual Accessibility Path

**Decision**: Implement both a graph canvas and keyboard-accessible node/edge/reference lists.

**Rationale**: React Flow provides keyboard and ARIA support, but the repository standard requires common workflows to remain ergonomic and accessible. List-based equivalents also simplify testing and allow admins to inspect large workflows without precise graph navigation.

**Alternatives Considered**:

- Graph-only editing: rejected for accessibility and testability.
- List-only editing: rejected because graph comprehension is central to workflow authoring.

## Decision 7: Validation Timing

**Decision**: Validation refreshes on demand and after successful saves. The page may show stale validation warnings when draft changes are dirty.

**Rationale**: This avoids unbounded polling while keeping publish decisions clear. It also lets QA prove stale evidence and stale validation behavior deterministically.

**Alternatives Considered**:

- Continuous background validation: rejected due to load and noisy state changes.
- Only manual validation: rejected because saved changes should visibly update validation freshness.
