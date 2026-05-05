import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { testBenchSuiteFixture } from "../../test/testBenchTestData";
import { RunLauncherPanel } from "./RunLauncherPanel";

describe("RunLauncherPanel", () => {
  it("defaults to mock mode and exposes approved safe mode metadata", async () => {
    const onLaunch = vi.fn();

    render(
      <RunLauncherPanel
        launchResult={null}
        onLaunch={onLaunch}
        suite={testBenchSuiteFixture}
      />,
    );

    expect(screen.getByLabelText("Safe execution mode")).toHaveValue("mock_model_tools");
    expect(screen.getByText("No external side effects")).toBeInTheDocument();

    await userEvent.selectOptions(
      screen.getByLabelText("Safe execution mode"),
      "real_dependency_probe",
    );
    expect(screen.getByText("Policy approval is required before execution.")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Launch run/ }));
    expect(onLaunch).toHaveBeenCalledWith(
      "/admin/app/test-bench/suites/suite-qa033-daily-briefing/runs",
      "real_dependency_probe",
    );
  });
});
