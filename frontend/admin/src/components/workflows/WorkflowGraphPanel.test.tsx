import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

import { workflowBuilderEnvelope } from "../../test/workflowBuilderTestData";
import { WorkflowGraphPanel } from "./WorkflowGraphPanel";

vi.mock("@xyflow/react", () => ({
  Background: () => <div data-testid="graph-background" />,
  Controls: () => <div data-testid="graph-controls" />,
  ReactFlow: ({
    children,
    edges,
    nodes,
  }: {
    children: ReactNode;
    edges: Array<{ id: string }>;
    nodes: Array<{ id: string }>;
  }) => (
    <div data-edge-count={edges.length} data-node-count={nodes.length}>
      {children}
    </div>
  ),
}));

describe("WorkflowGraphPanel", () => {
  it("renders graph canvas and keyboard-readable node and edge lists", () => {
    render(<WorkflowGraphPanel graph={workflowBuilderEnvelope.draft.graph} />);

    expect(screen.getByLabelText("Workflow graph canvas")).toBeInTheDocument();
    expect(screen.getByTestId("graph-controls")).toBeInTheDocument();
    expect(screen.getByText("Start briefing")).toBeInTheDocument();
    expect(screen.getByText("Weather branch")).toBeInTheDocument();
    expect(screen.getByText("start to calendar")).toBeInTheDocument();
    expect(screen.getByText("Wait for required branches")).toBeInTheDocument();
  });
});
