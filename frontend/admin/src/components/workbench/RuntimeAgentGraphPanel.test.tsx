import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { runtimeAgentGraphFixture } from "../../test/workbenchTestData";
import { AgentGraphPanel } from "../workflows/AgentGraphPanel";

vi.mock("@xyflow/react", () => ({
  Background: () => <div data-testid="graph-background" />,
  Controls: () => <div data-testid="graph-controls" />,
  ReactFlow: ({
    children,
    edges,
    nodes,
    onEdgeClick,
    onNodeClick,
  }: {
    children: ReactNode;
    edges: Array<{ id: string; label?: string }>;
    nodes: Array<{ data: { label: ReactNode }; id: string }>;
    onEdgeClick?: (event: unknown, edge: { id: string }) => void;
    onNodeClick?: (event: unknown, node: { id: string }) => void;
  }) => (
    <div data-testid="runtime-agent-react-flow">
      {nodes.map((node) => (
        <button
          key={node.id}
          onClick={() => onNodeClick?.({}, { id: node.id })}
          type="button"
        >
          {node.data.label}
        </button>
      ))}
      {edges.map((edge) => (
        <button
          key={edge.id}
          onClick={() => onEdgeClick?.({}, { id: edge.id })}
          type="button"
        >
          {edge.label}
        </button>
      ))}
      {children}
    </div>
  ),
}));

describe("RuntimeAgentGraphPanel", () => {
  it("renders runtime node statuses and accessible list equivalents", () => {
    render(
      <AgentGraphPanel
        graph={runtimeAgentGraphFixture}
        sourceLabel="Runtime run"
      />,
    );

    expect(screen.getByText("Runtime run communication")).toBeInTheDocument();
    expect(screen.getByText("retry_scheduled")).toBeInTheDocument();
    expect(screen.getByText("Running")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Node list" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Edge list" })).toBeInTheDocument();
  });

  it("shows safe runtime references for failed nodes and edges", async () => {
    const user = userEvent.setup();
    render(
      <AgentGraphPanel
        graph={runtimeAgentGraphFixture}
        sourceLabel="Runtime run"
      />,
    );

    const nodeList = screen.getByRole("heading", { name: "Node list" })
      .parentElement!;
    await user.click(
      within(nodeList).getByRole("button", { name: /Coordinator runtime node/ }),
    );
    expect(screen.getByText("Run step coordinator")).toBeInTheDocument();
    expect(screen.getByText("Attempt 1 is succeeded.")).toBeInTheDocument();

    const edgeList = screen.getByRole("heading", { name: "Edge list" })
      .parentElement!;
    await user.click(
      within(edgeList).getByRole("button", {
        name: /Coordinator to Specialist runtime path/,
      }),
    );
    expect(screen.getByText("Handoff to specialist")).toBeInTheDocument();
    expect(screen.getByText("Handoff contract handoff-contract is valid."))
      .toBeInTheDocument();
    expect(screen.getByText("Replay 1: handoff")).toBeInTheDocument();
    expect(screen.getByText("Coordinator sent safe context to Specialist."))
      .toBeInTheDocument();
    expect(screen.queryByText(/raw prompt|provider payload|secret value/i))
      .not.toBeInTheDocument();
  });
});
