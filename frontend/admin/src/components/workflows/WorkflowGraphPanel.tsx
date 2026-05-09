import "@xyflow/react/dist/style.css";

import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";

import type { WorkflowGraphPreview } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface WorkflowGraphPanelProps {
  graph: WorkflowGraphPreview;
}

export function WorkflowGraphPanel({ graph }: WorkflowGraphPanelProps) {
  const nodes: Node[] = graph.nodes.map((node) => ({
    data: {
      label: (
        <div className="workflow-node-label">
          <strong>{node.label}</strong>
          <small>{node.node_type}</small>
        </div>
      ),
    },
    id: node.node_id,
    position: { x: node.x, y: node.y },
    type: "default",
  }));
  const edges: Edge[] = graph.edges.map((edge) => ({
    id: edge.edge_id,
    label: edge.label ?? undefined,
    source: edge.source,
    target: edge.target,
  }));

  return (
    <section className="workflow-graph-panel" aria-labelledby="graph-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Graph</p>
          <h2 id="graph-title">Workflow structure</h2>
        </div>
        <Badge tone={graph.layout_is_authoritative ? "success" : "warning"}>
          {graph.layout_is_authoritative ? "authoritative" : "preview"}
        </Badge>
      </div>
      <p className="table-footer">{graph.accessibility_summary}</p>
      <div className="workflow-flow-canvas" aria-label="Workflow graph canvas">
        <ReactFlow
          edges={edges}
          fitView
          maxZoom={1.4}
          minZoom={0.3}
          nodes={nodes}
          nodesConnectable={false}
          nodesDraggable={false}
          panOnDrag={false}
          proOptions={{ hideAttribution: true }}
          zoomOnScroll={false}
        >
          <Background />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
      <div className="workflow-graph-lists">
        <section aria-labelledby="node-list-title">
          <h3 id="node-list-title">Nodes</h3>
          <ul className="workflow-node-list">
            {graph.nodes.map((node) => (
              <li key={node.node_id}>
                <div className="card-heading">
                  <strong>{node.label}</strong>
                  <Badge tone={toneFor(node.status)}>{node.status}</Badge>
                </div>
                <p>{node.summary}</p>
                <small>
                  {node.node_type}
                  {node.role_label ? ` / ${node.role_label}` : ""}
                </small>
              </li>
            ))}
          </ul>
        </section>
        <section aria-labelledby="edge-list-title">
          <h3 id="edge-list-title">Edges and joins</h3>
          <ul className="workflow-node-list">
            {graph.edges.map((edge) => (
              <li key={edge.edge_id}>
                <strong>
                  {edge.source} to {edge.target}
                </strong>
                <p>{edge.label ?? "Unlabeled edge"}</p>
                <small>{edge.condition_category ?? "default"}</small>
              </li>
            ))}
          </ul>
          {graph.join_policies.map((policy) => (
            <article className="join-policy-card" key={policy.policy_id}>
              <strong>{policy.label}</strong>
              <p>{policy.summary}</p>
              <small>{policy.required_branch_count} required branches</small>
            </article>
          ))}
        </section>
      </div>
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (status === "ready" || status === "published") {
    return "success";
  }
  if (status === "blocked" || status === "critical") {
    return "critical";
  }
  if (status === "warning" || status === "stale") {
    return "warning";
  }
  return "info";
}
