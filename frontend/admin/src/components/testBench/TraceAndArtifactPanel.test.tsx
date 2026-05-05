import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { testBenchRunDetailFixture } from "../../test/testBenchTestData";
import { TraceAndArtifactPanel } from "./TraceAndArtifactPanel";

describe("TraceAndArtifactPanel", () => {
  it("renders trace summaries and artifact references only", () => {
    render(<TraceAndArtifactPanel run={testBenchRunDetailFixture} />);

    expect(screen.getByText("Gateway summarized a blocked write decision.")).toBeInTheDocument();
    expect(screen.getByText("Redacted run summary artifact")).toBeInTheDocument();
    expect(screen.getByText("sha256:qa033artifactsummary")).toBeInTheDocument();
    expect(screen.queryByText(/storage path/)).not.toBeInTheDocument();
  });
});
