import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { workbenchExportFixture } from "../../test/workbenchTestData";
import { WorkbenchExportPanel } from "./WorkbenchExportPanel";

describe("WorkbenchExportPanel", () => {
  it("renders artifact reference and calls export callback", async () => {
    const onExport = vi.fn();
    render(
      <WorkbenchExportPanel
        exportSnapshot={workbenchExportFixture}
        onExport={onExport}
      />,
    );

    expect(screen.getByText(/operations-export:/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Export evidence" }));
    expect(onExport).toHaveBeenCalledTimes(1);
  });
});
