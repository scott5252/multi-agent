# Data Model: Agent Communication Graph Contracts And Projections

## AgentCommunicationGraph

- `graph_id`: Stable string combining source type and durable draft/version ID.
- `source`: `draft` or `published_version`.
- `state`: `ready`, `empty`, `partial`, or `denied` where applicable to safe response bodies.
- `partial`: Boolean flag for projections with safe metadata but incomplete topology.
- `provenance`: Durable source metadata for revision/version, scope, tenant, digest, and generated time.
- `nodes`: Ordered `AgentGraphNode` records.
- `edges`: Ordered `AgentGraphEdge` records.
- `badges`: Graph-level `AgentGraphBadge` records.
- `accessibility`: `AgentGraphAccessibility` summary and keyboard-readable node/edge lists.

## AgentGraphNode

- `node_id`: Stable `node:<node_key>` identifier.
- `node_key`: Existing workflow node key.
- `category`: Coordinator agent, sub-agent, tool, join, approval, handoff, terminal, subworkflow, or unknown.
- `label`: Safe display label.
- `summary`: Safe node purpose or fallback summary.
- `status`: Readiness/status label such as ready, warning, blocked, missing_reference, inactive, terminal, or unknown.
- `role_key`: Optional workflow role key.
- `layout`: Layout hint from editor position or deterministic fallback.
- `references`: Safe prompt/profile/provider/skill/subworkflow/contract reference summaries.
- `badges`: Safe status and validation badges.
- `accessibility_label`: Keyboard-readable node summary.

## AgentGraphEdge

- `edge_id`: Stable `edge:<edge_key>` identifier.
- `edge_key`: Existing workflow edge key.
- `source_node_id`: Source graph node ID.
- `target_node_id`: Target graph node ID.
- `category`: Communication category such as delegates_to, sends_context_to, returns_result_to, joins_at, hands_off_to, failure_routes_to, retries, approval_resumes, or transitions_to.
- `label`: Safe human label.
- `summary`: Safe explanation of the communication or transition.
- `contract_key`: Optional safe contract reference.
- `badges`: Safe status and validation badges.
- `accessibility_label`: Keyboard-readable edge summary.

## AgentGraphBadge

- `code`: Stable status or validation code.
- `severity`: info, warning, blocking, or critical.
- `label`: Safe short label.
- `summary`: Safe badge explanation.
- `blocking`: Whether the badge blocks readiness or publish.
- `source`: status, validation, reference, or provenance.

## AgentGraphReferenceSummary

- `reference_id`: Stable safe reference identifier.
- `reference_type`: prompt_profile, prompt, profile, provider, skill, contract, subworkflow, join_policy, approval_gate, or workflow_version.
- `label`: Safe display label.
- `summary`: Safe explanation.
- `status`: ready, warning, blocked, missing, unknown.
- `href`: Optional safe Admin path for known reference types.

## AgentGraphProvenance

- `source_type`: draft or published_version.
- `workflow_draft_id`: Present for draft projections.
- `workflow_version_bundle_id`: Present for published version projections.
- `workflow_lineage_id`: Durable lineage ID.
- `workflow_key`: Workflow key from the durable document or metadata.
- `revision`: Draft revision number or published display version.
- `source_revision_id`: Draft revision ID when available.
- `source_digest`: Draft document SHA or compiled bundle digest when available.
- `scope_type`: platform or tenant.
- `tenant_id`: Tenant ID for tenant-scoped records.
- `generated_at`: Projection timestamp.

## AgentGraphAccessibility

- `summary`: Safe graph overview.
- `node_summaries`: Tuple of keyboard-readable node summaries.
- `edge_summaries`: Tuple of keyboard-readable edge summaries.

## Relationships

- Draft graph projections read a `WorkflowDraftResponse.document`, latest
  revision metadata, and latest validation findings.
- Published graph projections read `WorkflowVersionResponse.summary_json` and
  compiled document metadata when available.
- Nodes and edges are not persisted by this spec.
