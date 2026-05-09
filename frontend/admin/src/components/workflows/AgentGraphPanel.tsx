import "@xyflow/react/dist/style.css";

import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import type {
  AgentCommunicationGraph,
  AgentGraphBadge,
  AgentGraphBadgeSeverity,
  AgentGraphEdge,
  AgentGraphEdgeCategory,
  AgentGraphNode,
  AgentGraphNodeCategory,
  AgentGraphReferenceSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface AgentGraphPanelProps {
  error?: string | null;
  graph: AgentCommunicationGraph | null;
  loading?: boolean;
  onRetry?: () => void;
  sourceLabel: string;
}

type Selection =
  | { id: string; kind: "node" }
  | { id: string; kind: "edge" }
  | null;

export function AgentGraphPanel({
  error = null,
  graph,
  loading = false,
  onRetry,
  sourceLabel,
}: AgentGraphPanelProps) {
  const [selection, setSelection] = useState<Selection>(null);

  useEffect(() => {
    setSelection(null);
  }, [graph?.graph_id]);

  const nodes: Node[] = useMemo(
    () =>
      (graph?.nodes ?? []).map((node) => ({
        className: `agent-graph-flow-node ${categoryClass(node.category)}`,
        data: {
          label: (
            <div className="agent-graph-node-label">
              <strong>{node.label}</strong>
              <small>{categoryLabel(node.category)}</small>
            </div>
          ),
        },
        id: node.node_id,
        position: { x: node.layout.x, y: node.layout.y },
        type: "default",
      })),
    [graph],
  );

  const edges: Edge[] = useMemo(
    () =>
      (graph?.edges ?? []).map((edge) => ({
        className: `agent-graph-flow-edge ${edgeCategoryClass(edge.category)}`,
        id: edge.edge_id,
        label: edgeLabel(edge),
        source: edge.source_node_id,
        target: edge.target_node_id,
      })),
    [graph],
  );

  const selected = selectedItem(graph, selection);

  if (loading) {
    return (
      <GraphPanelShell sourceLabel={sourceLabel}>
        <GraphState
          summary="Loading backend-owned communication graph data."
          title="Loading agent graph"
        />
      </GraphPanelShell>
    );
  }

  if (error) {
    return (
      <GraphPanelShell sourceLabel={sourceLabel}>
        <GraphState
          action={onRetry}
          actionLabel="Retry graph"
          summary={error}
          title="Agent graph unavailable"
        />
      </GraphPanelShell>
    );
  }

  if (!graph) {
    return (
      <GraphPanelShell sourceLabel={sourceLabel}>
        <GraphState
          summary="No graph response is available for this workflow record."
          title="No agent graph"
        />
      </GraphPanelShell>
    );
  }

  const isEmpty = graph.nodes.length === 0 && graph.edges.length === 0;

  return (
    <GraphPanelShell
      graph={graph}
      partial={graph.partial || graph.state === "partial"}
      sourceLabel={sourceLabel}
    >
      {isEmpty ? (
        <GraphState
          summary={graph.accessibility.summary}
          title="No communication graph nodes"
        />
      ) : (
        <div className="agent-graph-layout">
          <div
            aria-label={`${sourceLabel} communication graph canvas`}
            className="agent-graph-canvas"
          >
            <ReactFlow
              edges={edges}
              fitView
              maxZoom={1.35}
              minZoom={0.35}
              nodes={nodes}
              nodesConnectable={false}
              nodesDraggable={false}
              onEdgeClick={(_, edge) =>
                setSelection({ id: edge.id, kind: "edge" })
              }
              onNodeClick={(_, node) =>
                setSelection({ id: node.id, kind: "node" })
              }
              panOnDrag
              proOptions={{ hideAttribution: true }}
              zoomOnScroll={false}
            >
              <Background />
              <Controls showInteractive={false} />
            </ReactFlow>
          </div>
          <GraphDetail selected={selected} />
          <GraphLists
            graph={graph}
            selection={selection}
            setSelection={setSelection}
          />
        </div>
      )}
    </GraphPanelShell>
  );
}

function GraphPanelShell({
  children,
  graph,
  partial = false,
  sourceLabel,
}: {
  children: ReactNode;
  graph?: AgentCommunicationGraph;
  partial?: boolean;
  sourceLabel: string;
}) {
  return (
    <section className="agent-graph-panel" aria-labelledby="agent-graph-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Agent graph</p>
          <h2 id="agent-graph-title">{sourceLabel} communication</h2>
        </div>
        <div className="agent-graph-status">
          {graph ? <Badge tone={stateTone(graph.state)}>{graph.state}</Badge> : null}
          {partial ? <Badge tone="warning">partial</Badge> : null}
        </div>
      </div>
      {graph ? <p className="table-footer">{graph.accessibility.summary}</p> : null}
      {graph?.badges.length ? <BadgeRow badges={graph.badges} /> : null}
      {children}
    </section>
  );
}

function GraphState({
  action,
  actionLabel,
  summary,
  title,
}: {
  action?: () => void;
  actionLabel?: string;
  summary: string;
  title: string;
}) {
  return (
    <div className="agent-graph-state" role="status">
      <strong>{title}</strong>
      <p>{summary}</p>
      {action ? (
        <Button onClick={action} type="button" variant="secondary">
          {actionLabel ?? "Retry"}
        </Button>
      ) : null}
    </div>
  );
}

function GraphLists({
  graph,
  selection,
  setSelection,
}: {
  graph: AgentCommunicationGraph;
  selection: Selection;
  setSelection: (selection: Selection) => void;
}) {
  return (
    <div className="agent-graph-lists">
      <section aria-labelledby="agent-node-list-title">
        <h3 id="agent-node-list-title">Node list</h3>
        <ul className="agent-graph-list">
          {graph.nodes.map((node) => (
            <li key={node.node_id}>
              <button
                aria-pressed={
                  selection?.kind === "node" && selection.id === node.node_id
                }
                className="agent-graph-list-button"
                onClick={() => setSelection({ id: node.node_id, kind: "node" })}
                type="button"
              >
                <span>
                  <strong>{node.label}</strong>
                  <small>{node.accessibility_label}</small>
                </span>
                <Badge tone={statusTone(node.status)}>{node.status}</Badge>
              </button>
            </li>
          ))}
        </ul>
      </section>
      <section aria-labelledby="agent-edge-list-title">
        <h3 id="agent-edge-list-title">Edge list</h3>
        <ul className="agent-graph-list">
          {graph.edges.map((edge) => (
            <li key={edge.edge_id}>
              <button
                aria-pressed={
                  selection?.kind === "edge" && selection.id === edge.edge_id
                }
                className="agent-graph-list-button"
                onClick={() => setSelection({ id: edge.edge_id, kind: "edge" })}
                type="button"
              >
                <span>
                  <strong>{edge.label}</strong>
                  <small>{edge.accessibility_label}</small>
                </span>
                <Badge tone={statusTone(edge.status)}>{edge.status}</Badge>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function GraphDetail({
  selected,
}: {
  selected: AgentGraphNode | AgentGraphEdge | null;
}) {
  if (!selected) {
    return (
      <aside
        aria-labelledby="agent-graph-detail-title"
        className="agent-graph-detail"
      >
        <p className="eyebrow">Selection</p>
        <h3 id="agent-graph-detail-title">Select a node or edge</h3>
        <p>Choose an item from the graph or list to inspect safe details.</p>
      </aside>
    );
  }

  const isNode = "node_id" in selected;
  const title = selected.label;
  const category = isNode
    ? categoryLabel(selected.category)
    : edgeCategoryLabel(selected.category);
  const references = selected.references ?? [];

  return (
    <aside
      aria-labelledby="agent-graph-detail-title"
      className="agent-graph-detail"
    >
      <p className="eyebrow">{isNode ? "Node detail" : "Edge detail"}</p>
      <h3 id="agent-graph-detail-title">{title}</h3>
      <div className="agent-graph-detail-meta">
        <Badge tone="info">{category}</Badge>
        {"status" in selected ? (
          <Badge tone={statusTone(selected.status)}>{selected.status}</Badge>
        ) : null}
      </div>
      <p>{selected.summary}</p>
      {selected.badges.length ? <BadgeRow badges={selected.badges} /> : null}
      {references.length ? <ReferenceList references={references} /> : null}
    </aside>
  );
}

function BadgeRow({ badges }: { badges: AgentGraphBadge[] }) {
  return (
    <ul className="agent-graph-badges" aria-label="Graph badges">
      {badges.map((badge) => (
        <li key={`${badge.source}:${badge.code}`}>
          <Badge tone={badgeTone(badge.severity)}>{badge.label}</Badge>
          <span>{badge.summary}</span>
        </li>
      ))}
    </ul>
  );
}

function ReferenceList({
  references,
}: {
  references: AgentGraphReferenceSummary[];
}) {
  return (
    <div className="agent-graph-references">
      <h4>References</h4>
      <ul>
        {references.map((reference) => (
          <li key={reference.reference_id}>
            <strong>{reference.label}</strong>
            <p>{reference.summary}</p>
            <small>
              {reference.reference_type} / {reference.status}
            </small>
            {reference.href ? <a href={reference.href}>Open reference</a> : null}
          </li>
        ))}
      </ul>
    </div>
  );
}

function selectedItem(
  graph: AgentCommunicationGraph | null,
  selection: Selection,
) {
  if (!graph || !selection) {
    return null;
  }
  if (selection.kind === "node") {
    return graph.nodes.find((node) => node.node_id === selection.id) ?? null;
  }
  return graph.edges.find((edge) => edge.edge_id === selection.id) ?? null;
}

function edgeLabel(edge: AgentGraphEdge): string {
  return edge.label || edgeCategoryLabel(edge.category);
}

function categoryLabel(category: AgentGraphNodeCategory): string {
  return {
    approval: "Approval",
    coordinator_agent: "Coordinator agent",
    handoff: "Handoff",
    join: "Join",
    sub_agent: "Sub-agent",
    subworkflow: "Subworkflow",
    terminal: "Terminal",
    tool: "Tool",
    unknown: "Unknown",
  }[category];
}

function edgeCategoryLabel(category: AgentGraphEdgeCategory): string {
  return {
    approval_resumes: "Approval resumes",
    delegates_to: "Delegates",
    failure_routes_to: "Failure routes",
    hands_off_to: "Hands off",
    joins_at: "Joins",
    returns_result_to: "Returns result",
    retries: "Retries",
    sends_context_to: "Sends context",
    transitions_to: "Transitions",
  }[category];
}

function categoryClass(category: AgentGraphNodeCategory): string {
  return `agent-node-${category.replaceAll("_", "-")}`;
}

function edgeCategoryClass(category: AgentGraphEdgeCategory): string {
  return `agent-edge-${category.replaceAll("_", "-")}`;
}

function badgeTone(
  severity: AgentGraphBadgeSeverity,
): "info" | "warning" | "critical" {
  if (severity === "critical" || severity === "blocking") {
    return "critical";
  }
  if (severity === "warning") {
    return "warning";
  }
  return "info";
}

function statusTone(
  status: string,
): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed", "published", "active"].includes(status)) {
    return "success";
  }
  if (["completed", "succeeded"].includes(status)) {
    return "success";
  }
  if (
    ["blocked", "failed", "critical", "denied", "manual_resolution_required"].includes(
      status,
    )
  ) {
    return "critical";
  }
  if (
    [
      "warning",
      "stale",
      "partial",
      "missing",
      "paused",
      "waiting",
      "retry_scheduled",
      "skipped",
      "unavailable",
    ].includes(status)
  ) {
    return "warning";
  }
  return "info";
}

function stateTone(
  state: string,
): "info" | "success" | "warning" | "critical" {
  if (state === "ready") {
    return "success";
  }
  if (state === "partial" || state === "empty") {
    return "warning";
  }
  if (state === "denied") {
    return "critical";
  }
  return "info";
}
