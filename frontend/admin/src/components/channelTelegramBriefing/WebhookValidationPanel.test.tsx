import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { channelDashboard, channelMutation } from "../../test/channelTelegramBriefingTestData";
import { WebhookValidationPanel } from "./WebhookValidationPanel";

describe("WebhookValidationPanel", () => {
  it("shows validation evidence and triggers explicit action", async () => {
    const validate = vi.fn();
    render(
      <WebhookValidationPanel
        configs={channelDashboard.tenant_configs}
        diagnostics={channelDashboard.webhook_diagnostics}
        result={channelMutation}
        onValidate={validate}
      />,
    );

    expect(screen.getByText("Mock-safe receipt categories are current")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Validate Acme" }));
    expect(validate).toHaveBeenCalledOnce();
  });
});
