import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { testBenchRunDetailFixture } from "../../test/testBenchTestData";
import { RunDetailPanel } from "./RunDetailPanel";

describe("RunDetailPanel", () => {
  it("shows failing diagnostics without unsafe payloads", () => {
    render(<RunDetailPanel run={testBenchRunDetailFixture} />);

    expect(screen.getByText("Blocked side-effect assertion failed")).toBeInTheDocument();
    expect(screen.getByText("trace_steps[side-effect].blocked_side_effects")).toBeInTheDocument();
    expect(screen.queryByText(/raw completion/)).not.toBeInTheDocument();
    expect(screen.queryByText(/connector request/)).not.toBeInTheDocument();
  });
});
