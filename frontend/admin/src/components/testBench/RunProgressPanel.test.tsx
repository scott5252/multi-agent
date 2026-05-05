import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { testBenchRunDetailFixture } from "../../test/testBenchTestData";
import { RunProgressPanel } from "./RunProgressPanel";

describe("RunProgressPanel", () => {
  it("uses backend progress snapshots", () => {
    render(<RunProgressPanel run={testBenchRunDetailFixture} />);

    expect(screen.getByText("Backend run state reports the current terminal status.")).toBeInTheDocument();
    expect(screen.getByText("2/2")).toBeInTheDocument();
    expect(screen.getByText("audit-progress-run-qa033-failing")).toBeInTheDocument();
  });
});
