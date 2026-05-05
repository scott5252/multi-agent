import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { channelDashboard } from "../../test/channelTelegramBriefingTestData";
import { DeliveryDiagnosticsPanel } from "./DeliveryDiagnosticsPanel";

describe("DeliveryDiagnosticsPanel", () => {
  it("renders bounded delivery evidence and safe run action", async () => {
    const openRun = vi.fn();
    render(
      <DeliveryDiagnosticsPanel
        attempts={channelDashboard.delivery_attempts}
        receipts={channelDashboard.webhook_diagnostics}
        onOpenRun={openRun}
      />,
    );

    expect(screen.getByText("No delivery issue")).toBeInTheDocument();
    expect(screen.getByText("mocked")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Open Run Status" }));
    expect(openRun).toHaveBeenCalledWith("/admin/app/channels/runs/qa036-run-morning-briefing");
  });
});
