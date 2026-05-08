import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { workflowBuilderEnvelope } from "../../test/workflowBuilderTestData";
import { WorkflowJsonInspector } from "./WorkflowJsonInspector";
import { WorkflowRevisionPanel } from "./WorkflowRevisionPanel";

describe("WorkflowRevisionPanel and WorkflowJsonInspector", () => {
  it("renders safe revision history and redacted JSON preview", () => {
    render(
      <>
        <WorkflowRevisionPanel revisions={workflowBuilderEnvelope.revisions} />
        <WorkflowJsonInspector inspector={workflowBuilderEnvelope.json_inspector!} />
      </>,
    );

    expect(screen.getByText("Immutable draft history")).toBeInTheDocument();
    expect(screen.getByText("audit-workflow-revision-current-qa030"))
      .toBeInTheDocument();
    expect(screen.getByText("Read-only preview")).toBeInTheDocument();
    expect(screen.getByText("artifact-ref-qa030-json-preview")).toBeInTheDocument();
    expect(screen.queryByText(/qa030-secret-value/i)).not.toBeInTheDocument();
  });
});
