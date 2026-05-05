import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { testBenchSuiteFixture } from "../../test/testBenchTestData";
import { AssertionAndTargetPanel } from "./AssertionAndTargetPanel";

describe("AssertionAndTargetPanel", () => {
  it("renders backend-owned target and assertion descriptors", () => {
    render(
      <AssertionAndTargetPanel
        metadata={testBenchSuiteFixture.run_launcher}
        targetBinding={testBenchSuiteFixture.target_binding}
      />,
    );

    expect(screen.getByText("Daily briefing draft")).toBeInTheDocument();
    expect(screen.getByText("Contract shape")).toBeInTheDocument();
    expect(screen.getByText("response.summary.status")).toBeInTheDocument();
    expect(screen.queryByText(/raw completion/)).not.toBeInTheDocument();
  });
});
