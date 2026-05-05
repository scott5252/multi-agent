import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { testBenchGateFixture } from "../../test/testBenchTestData";
import { PublishGateEvidencePanel } from "./PublishGateEvidencePanel";

describe("PublishGateEvidencePanel", () => {
  it("shows stale evidence as blocking and refreshable", async () => {
    const onRefreshGate = vi.fn();

    render(
      <PublishGateEvidencePanel
        gates={[testBenchGateFixture]}
        onRefreshGate={onRefreshGate}
        refreshResult={null}
      />,
    );

    expect(screen.getByText("Latest run is tied to an older draft revision.")).toBeInTheDocument();
    expect(screen.getByText("stale")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Refresh evidence/ }));
    expect(onRefreshGate).toHaveBeenCalledWith(
      "/admin/app/test-bench/gates/qa033-required-suite/refresh",
    );
  });
});
