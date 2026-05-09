import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import {
  agentGraphFixture,
  partialPublishedAgentGraphFixture,
  publishedAgentGraphFixture,
} from "../../test/workflowBuilderTestData";
import { AgentGraphPanel } from "./AgentGraphPanel";

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
    <div data-testid="agent-react-flow">
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

const unsafeMarkers = [
  "raw prompt",
  "raw completion",
  "provider payload",
  "secret value",
  "private channel message",
  "memory contents",
  "raw tool",
];

function expectSafeVisibleCopy(container: HTMLElement) {
  const text = container.textContent?.toLowerCase() ?? "";
  for (const marker of unsafeMarkers) {
    expect(text).not.toContain(marker);
  }
}

describe("AgentGraphPanel", () => {
  it("renders draft graph categories, edge labels, badges, and list equivalents", () => {
    const { container } = render(
      <AgentGraphPanel
        graph={agentGraphFixture}
        sourceLabel="Draft"
      />,
    );

    expect(screen.getByText("Draft communication")).toBeInTheDocument();
    expect(screen.getByLabelText("Draft communication graph canvas"))
      .toBeInTheDocument();
    expect(screen.getByText("Coordinator agent")).toBeInTheDocument();
    expect(screen.getByText("Sub-agent")).toBeInTheDocument();
    expect(screen.getByText("Tool")).toBeInTheDocument();
    expect(screen.getByText("Join")).toBeInTheDocument();
    expect(screen.getByText("Approval")).toBeInTheDocument();
    expect(screen.getByText("Handoff")).toBeInTheDocument();
    expect(screen.getByText("Terminal")).toBeInTheDocument();
    expect(screen.getAllByText("Delegates").length).toBeGreaterThan(0);
    expect(screen.getByText("Projected graph")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Node list" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Edge list" })).toBeInTheDocument();
    expectSafeVisibleCopy(container);
  });

  it("shows published provenance and partial graph state", () => {
    render(
      <AgentGraphPanel
        graph={partialPublishedAgentGraphFixture}
        sourceLabel="Published version"
      />,
    );

    expect(screen.getByText("Published version communication"))
      .toBeInTheDocument();
    expect(screen.getAllByText("partial").length).toBeGreaterThan(0);
    expect(screen.getByText("Partial graph")).toBeInTheDocument();
  });

  it("updates details when selecting nodes and edges", async () => {
    const user = userEvent.setup();
    render(
      <AgentGraphPanel
        graph={publishedAgentGraphFixture}
        sourceLabel="Published version"
      />,
    );

    await user.click(
      screen.getAllByRole("button", { name: /Calendar specialist/ })[0],
    );
    const detail = screen.getByRole("heading", { name: "Calendar specialist" })
      .parentElement!;
    expect(within(detail).getByText("Sub-agent")).toBeInTheDocument();
    expect(
      within(detail).getByText("Reviews calendar-safe context."),
    ).toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: /^Hands off$/ })[0]);
    const edgeDetail = screen.getByRole("heading", { name: "Hands off" })
      .parentElement!;
    expect(within(edgeDetail).getByText("Approval releases the handoff summary."))
      .toBeInTheDocument();
    expect(within(edgeDetail).getAllByText("Hands off").length)
      .toBeGreaterThan(0);
  });

  it("supports keyboard-readable list selection and named regions", async () => {
    const user = userEvent.setup();
    render(
      <AgentGraphPanel
        graph={agentGraphFixture}
        sourceLabel="Draft"
      />,
    );

    const nodeList = screen.getByRole("heading", { name: "Node list" })
      .parentElement!;
    const coordinator = within(nodeList).getByRole("button", {
      name: /Coordinator agent node Coordinator is ready/,
    });
    coordinator.focus();
    await user.keyboard("{Enter}");

    expect(coordinator).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("heading", { name: "Coordinator" }))
      .toBeInTheDocument();
  });

  it("renders loading, error, and empty states truthfully", () => {
    const { rerender } = render(
      <AgentGraphPanel
        graph={null}
        loading
        sourceLabel="Draft"
      />,
    );
    expect(screen.getByText("Loading agent graph")).toBeInTheDocument();

    rerender(
      <AgentGraphPanel
        error="Graph access denied"
        graph={null}
        sourceLabel="Draft"
      />,
    );
    expect(screen.getByText("Agent graph unavailable")).toBeInTheDocument();
    expect(screen.getByText("Graph access denied")).toBeInTheDocument();

    rerender(
      <AgentGraphPanel
        graph={{
          ...agentGraphFixture,
          accessibility: {
            edge_summaries: [],
            node_summaries: [],
            summary: "Draft graph has no communication nodes.",
          },
          edges: [],
          nodes: [],
          state: "empty",
        }}
        sourceLabel="Draft"
      />,
    );
    expect(screen.getByText("No communication graph nodes")).toBeInTheDocument();
    expect(screen.getAllByText("Draft graph has no communication nodes.").length)
      .toBeGreaterThan(0);
  });
});
