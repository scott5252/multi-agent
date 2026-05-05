import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { skillLifecycleDashboardFixture } from "../../test/skillLifecycleTestData";
import { BindingAndDiagnosticsPanel } from "./BindingAndDiagnosticsPanel";

describe("BindingAndDiagnosticsPanel", () => {
  it("shows read-only binding and diagnostic summaries without raw tool output", async () => {
    const onDiagnostic = vi.fn();
    const onPreview = vi.fn();

    render(
      <BindingAndDiagnosticsPanel
        bindingResult={null}
        diagnostics={skillLifecycleDashboardFixture.skill_execution_diagnostics}
        onDiagnostic={onDiagnostic}
        onPreview={onPreview}
        preview={skillLifecycleDashboardFixture.binding_preview}
      />,
    );

    expect(screen.getByText("Eligibility and diagnostics")).toBeInTheDocument();
    expect(screen.getByText("Daily briefing workflow")).toBeInTheDocument();
    expect(screen.getAllByText("calendar.read")).toHaveLength(2);
    expect(screen.getByText("email.send")).toBeInTheDocument();
    expect(screen.queryByText(/raw tool output/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Preview binding/ }));
    await userEvent.click(screen.getByRole("button", { name: /Run diagnostic/ }));

    expect(onPreview).toHaveBeenCalledTimes(1);
    expect(onDiagnostic).toHaveBeenCalledTimes(1);
  });
});
