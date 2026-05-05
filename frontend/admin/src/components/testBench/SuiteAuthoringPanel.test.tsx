import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { testBenchSuiteFixture } from "../../test/testBenchTestData";
import { SuiteAuthoringPanel } from "./SuiteAuthoringPanel";

describe("SuiteAuthoringPanel", () => {
  it("renders safe suite and case authoring summaries", async () => {
    const onSaveSuite = vi.fn();
    const onSaveCase = vi.fn();

    render(
      <SuiteAuthoringPanel
        caseResult={null}
        onSaveCase={onSaveCase}
        onSaveSuite={onSaveSuite}
        suite={testBenchSuiteFixture}
        suiteResult={null}
      />,
    );

    expect(screen.getByText("Suite and case forms")).toBeInTheDocument();
    expect(screen.getByText("Fixture includes weather metadata summary.")).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save case/ }));

    expect(onSaveCase).toHaveBeenCalledWith(
      "/admin/app/test-bench/suites/suite-qa033-daily-briefing/cases",
      testBenchSuiteFixture.cases[0],
    );
  });
});
