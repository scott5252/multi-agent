import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { channelDashboard } from "../../test/channelTelegramBriefingTestData";
import { ReadinessCardGrid } from "./ReadinessCardGrid";
import { TelegramConfigPanel } from "./TelegramConfigPanel";

describe("readiness and config panels", () => {
  it("renders safe readiness and reference labels", () => {
    render(<ReadinessCardGrid readiness={channelDashboard.readiness} />);

    expect(screen.getByRole("heading", { name: "Readiness" })).toBeInTheDocument();
    expect(screen.getByText("Telegram")).toBeInTheDocument();
    expect(screen.getByText("audit-qa036-readiness-acme")).toBeInTheDocument();
  });

  it("renders tenant config without unsafe values", () => {
    render(
      <TelegramConfigPanel
        configs={channelDashboard.tenant_configs}
        result={null}
        onSave={vi.fn()}
      />,
    );

    expect(screen.getByText("Telegram provider ref ready")).toBeInTheDocument();
    expect(screen.queryByText(/bot token|webhook secret/i)).not.toBeInTheDocument();
  });
});
