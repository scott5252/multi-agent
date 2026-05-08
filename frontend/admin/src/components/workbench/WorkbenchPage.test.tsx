import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  workbenchEnvelopeFixture,
  workbenchExportFixture,
} from "../../test/workbenchTestData";
import { WorkbenchPage } from "./WorkbenchPage";

describe("WorkbenchPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads platform workbench summaries without unsafe payloads", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => workbenchEnvelopeFixture,
      }),
    );

    render(<WorkbenchPage workbenchUrl="/admin/app/operations.json" />);

    await waitFor(() => {
      expect(screen.getByText("Operations workbench")).toBeInTheDocument();
    });
    expect(screen.getByText("Workflow run 11111111 from live audit evidence")).toBeInTheDocument();
    expect(screen.getByText("Redacted signals")).toBeInTheDocument();
    expect(screen.queryByText(/qa029/i)).not.toBeInTheDocument();
  });

  it("requests export snapshots from backend-owned actions", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workbenchEnvelopeFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workbenchExportFixture,
        }),
    );

    render(<WorkbenchPage workbenchUrl="/admin/app/operations.json" />);

    await screen.findByText("Operations workbench");
    await userEvent.click(screen.getByRole("button", { name: "Export evidence" }));

    await waitFor(() => {
      expect(screen.getByText(/operations-export:/)).toBeInTheDocument();
    });
  });
});
