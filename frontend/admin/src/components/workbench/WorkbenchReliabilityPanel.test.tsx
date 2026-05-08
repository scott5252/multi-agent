import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { workbenchEnvelopeFixture } from "../../test/workbenchTestData";
import { WorkbenchReliabilityPanel } from "./WorkbenchReliabilityPanel";

describe("WorkbenchReliabilityPanel", () => {
  it("renders recovery state and confirmation metadata", () => {
    render(
      <WorkbenchReliabilityPanel reliability={workbenchEnvelopeFixture.reliability} />,
    );

    expect(screen.getByText("Open breakers")).toBeInTheDocument();
    expect(screen.getByText("1 open breaker records.")).toBeInTheDocument();
  });
});
