import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  usageDashboard,
  usageDrilldown,
  usageExportSummary,
} from "../../test/usageTestData";
import { UsagePage } from "./UsagePage";

describe("UsagePage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads dashboard, drilldown, and export evidence", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ ok: true, json: async () => usageDashboard })
        .mockResolvedValueOnce({ ok: true, json: async () => usageDrilldown })
        .mockResolvedValueOnce({ ok: true, json: async () => usageExportSummary }),
    );

    render(<UsagePage usageUrl="/admin/app/usage/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Usage and Cost Analytics" });
    expect(screen.getByText("Total tokens")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "View" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/admin/app/usage/events.json"),
        expect.objectContaining({ credentials: "same-origin" }),
      );
    });

    await userEvent.click(screen.getAllByRole("button", { name: /Export CSV|Create export/ })[0]);

    await waitFor(() => {
      expect(screen.getByText("usage-export-artifact-qa035")).toBeInTheDocument();
    });
    expect(screen.queryByText(/qa035-secret-value|raw prompt/i)).not.toBeInTheDocument();
  });
});
