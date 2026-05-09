# Research: Agent Communication Graph Contracts And Projections

## Decision: Reuse Workflow Registry Authorization

**Rationale**: Draft and published workflow routes already enforce principal
visibility, tenant scope, sharing, not-found, and fail-closed behavior. Keeping
graph endpoints under the workflow router avoids a second authorization model.

**Alternatives considered**: A separate router namespace was rejected because it
would duplicate tenant-visibility logic and increase drift before the React UI
uses the contract.

## Decision: Add Dedicated Agent Graph Schemas

**Rationale**: The existing graph preview schema is editor-oriented and too
small for agent/sub-agent categories, reference summaries, published provenance,
accessibility lists, and partial graph state. A dedicated schema module provides
a stable UI contract without breaking existing workflow builder previews.

**Alternatives considered**: Extending `workflow_editor.py` was rejected because
it would blur existing generic preview semantics with the new agent
communication model.

## Decision: Project From Existing Durable Records

**Rationale**: Draft documents already contain roles, prompt/profile references,
skills, contracts, nodes, edges, joins, approvals, subworkflows, editor
positions, and validation findings. Published bundles store the compiled
document or safe summary metadata. This is enough for Spec 065.

**Alternatives considered**: New graph tables or migrations were rejected for
Spec 065 because they would add idle persistence before runtime evidence gaps
are proven by Specs 067 and 068.

## Decision: Partial Published Graph State

**Rationale**: Older or manually created published bundle rows may not include a
full compiled document in metadata. In that case the API should return safe
published metadata with `partial=true` instead of inventing topology.

**Alternatives considered**: Returning 404 was rejected because the version
exists and is authorized. Fabricating nodes from counts was rejected because it
would violate the live-data and no-sample-graph requirements.

## Decision: Safe-Text Enforcement At Schema Boundary

**Rationale**: Future UI rendering depends on all labels and summaries being
safe by construction. Reusing Admin safe-text conventions and explicit unsafe
marker checks keeps tests deterministic and prevents accidental raw prompt,
completion, credential, provider, memory, channel, or tool payload exposure.

**Alternatives considered**: Trusting source workflow metadata was rejected
because authoring documents can contain user-entered labels and descriptions.
