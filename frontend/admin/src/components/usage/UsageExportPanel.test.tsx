import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { usageExportSummary } from "../../test/usageTestData";
import { UsageExportPanel } from "./UsageExportPanel";

describe("UsageExportPanel", () => {
  it("renders audited export metadata and create action", async () => {
    const onExport = vi.fn();

    render(
      <UsageExportPanel
        exportResult={usageExportSummary}
        exports={[usageExportSummary]}
        onExport={onExport}
      />,
    );

    expect(
      screen.getByText("usage-export:56000000-0000-0000-0000-000000000056"),
    ).toBeInTheDocument();
    expect(screen.getByText("audit-usage-qa056-export-created")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Create export/ }));
    expect(onExport).toHaveBeenCalledOnce();
  });
});
