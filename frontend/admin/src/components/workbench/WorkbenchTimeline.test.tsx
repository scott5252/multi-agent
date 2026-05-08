import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { workbenchEnvelopeFixture } from "../../test/workbenchTestData";
import { WorkbenchTimeline } from "./WorkbenchTimeline";

describe("WorkbenchTimeline", () => {
  it("renders run timeline, branch, gateway, tool, and delivery summaries", () => {
    render(<WorkbenchTimeline runDebug={workbenchEnvelopeFixture.run_debug!} />);

    expect(screen.getByText("Workflow run 11111111 from live audit evidence")).toBeInTheDocument();
    expect(screen.getByText("Gateway evidence")).toBeInTheDocument();
    expect(screen.getByText("OpenAI provider")).toBeInTheDocument();
    expect(screen.getByText("Weather live summary")).toBeInTheDocument();
    expect(screen.getByText("Live briefing alias")).toBeInTheDocument();
  });
});
