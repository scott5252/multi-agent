import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { workbenchEnvelopeFixture } from "../../test/workbenchTestData";
import { WorkbenchSummaryGrid } from "./WorkbenchSummaryGrid";

describe("WorkbenchSummaryGrid", () => {
  it("renders health, likely cause, and safe polling summaries", () => {
    render(
      <WorkbenchSummaryGrid
        cards={workbenchEnvelopeFixture.summary_cards}
        causes={workbenchEnvelopeFixture.likely_causes}
        panels={workbenchEnvelopeFixture.health_panels}
      />,
    );

    expect(screen.getByText("System Health")).toBeInTheDocument();
    expect(screen.getByText("Gateway")).toBeInTheDocument();
    expect(screen.getByText(/safe polling available/)).toBeInTheDocument();
  });
});
