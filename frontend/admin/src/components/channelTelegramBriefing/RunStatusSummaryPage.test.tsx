import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { runStatus } from "../../test/channelTelegramBriefingTestData";
import { RunStatusSummaryPage } from "./RunStatusSummaryPage";

describe("RunStatusSummaryPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads safe user-facing run status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce({ ok: true, json: async () => runStatus }),
    );

    render(
      <RunStatusSummaryPage runStatusUrl="/admin/app/channels/runs/qa036-run-morning-briefing/status.json" />,
    );

    await screen.findByRole("heading", { name: "Daily briefing workflow" });
    expect(screen.getByText("Review safe progress only.")).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt|run result/i)).not.toBeInTheDocument();
  });
});
