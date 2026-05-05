import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { workbenchEnvelopeFixture } from "../../test/workbenchTestData";
import { WorkbenchTimeline } from "./WorkbenchTimeline";

describe("WorkbenchTimeline", () => {
  it("renders run timeline, branch, gateway, tool, and delivery summaries", () => {
    render(<WorkbenchTimeline runDebug={workbenchEnvelopeFixture.run_debug!} />);

    expect(screen.getByText("Daily briefing graph run")).toBeInTheDocument();
    expect(screen.getByText("Weather branch")).toBeInTheDocument();
    expect(screen.getByText("OpenAI provider")).toBeInTheDocument();
    expect(screen.getByText("Daily briefing weather")).toBeInTheDocument();
    expect(screen.getByText("Morning briefing alias")).toBeInTheDocument();
  });
});
