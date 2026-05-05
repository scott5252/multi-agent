import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { channelDashboard, channelMutation } from "../../test/channelTelegramBriefingTestData";
import { AliasManagementPanel } from "./AliasManagementPanel";

describe("AliasManagementPanel", () => {
  it("renders alias readiness and lifecycle controls", async () => {
    const action = vi.fn();
    const create = vi.fn();
    render(
      <AliasManagementPanel
        aliases={channelDashboard.aliases}
        result={channelMutation}
        onAction={action}
        onCreate={create}
      />,
    );

    expect(screen.getByText("Morning briefing")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Create Alias" }));
    await userEvent.click(screen.getByRole("button", { name: "Refresh" }));
    expect(create).toHaveBeenCalledOnce();
    expect(action).toHaveBeenCalledOnce();
  });
});
