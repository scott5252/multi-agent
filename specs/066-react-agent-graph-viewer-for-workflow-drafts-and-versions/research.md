# Research: React Agent Graph Viewer For Workflow Drafts And Versions

## Decision: Reuse Existing Workflow Builder Entry Points

**Rationale**: `WorkflowBuilderPage` already handles `/admin/app/workflows`, draft detail links, version detail summaries, registry state, validation panels, publish panels, JSON inspector, and local-principal Admin shell behavior. Embedding the agent graph viewer there keeps the feature discoverable without adding navigation or route authorization complexity.

**Alternatives considered**: A new `/admin/app/agent-graphs` workspace was rejected because it would duplicate workflow navigation and introduce new empty/denied state surfaces. Replacing the existing `WorkflowGraphPanel` was rejected because the legacy graph preview is still useful for authoring structure.

## Decision: Add AgentCommunicationGraph To Generated React Types

**Rationale**: The current generated React Admin API file includes workflow builder graph preview types but not the Spec 065 Agent Communication Graph schemas. The viewer must consume typed graph data, so the generator should import `AgentCommunicationGraph` and emit related nested types and a runtime assertion helper.

**Alternatives considered**: Hand-written TypeScript interfaces were rejected because they would drift from backend Pydantic contracts. Using `unknown` at the component boundary was rejected because strict mode and tests should catch contract mismatches.

## Decision: Add Client Helpers For Draft And Version Graph Fetches

**Rationale**: Existing frontend API functions centralize same-origin fetches, safe error extraction, and generated assertion helpers. Draft and version graph fetches should follow that pattern for loading, denied, not-found, and problem-detail behavior.

**Alternatives considered**: Fetching inside the component without helpers was rejected because it would duplicate error handling. Adding new backend React envelope routes was rejected because Spec 065 already exposed route families that are sufficient for Spec 066.

## Decision: Build A Reusable AgentGraphPanel

**Rationale**: Drafts, published versions, and future runtime graph overlays need a shared graph display surface with common category styling, edge labels, selection, badges, references, and accessible lists. A reusable component under workflow components matches current ownership and can be expanded by Spec 067.

**Alternatives considered**: Extending `WorkflowGraphPanel` directly was rejected because workflow builder graph preview and Agent Communication Graph have different contracts and detail needs. Creating a broad shared graph package was deferred until runtime graph reuse proves the abstraction boundary.

## Decision: Keep Accessible Lists First-Class

**Rationale**: The roadmap explicitly requires keyboard-readable node and edge list equivalents. The lists should be visible or immediately reachable within the panel, not hidden behind canvas-only interactions.

**Alternatives considered**: A keyboard-only toggle was rejected because it makes accessibility evidence harder to inspect and risks hiding equivalent content from reviewers.

## Decision: Validate With Seeded Live Data And Browser Screenshots

**Rationale**: Spec 066 is primarily user-facing. QA must prove desktop and mobile legibility, selected detail behavior, loading/empty/partial/denied states, and redaction-safe visible copy against deterministic local data.

**Alternatives considered**: Component-only validation was rejected because it cannot catch layout overlap, viewport issues, or FastAPI-served asset integration.
