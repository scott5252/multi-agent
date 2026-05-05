import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  channelDashboard,
  linkTokenResult,
} from "../../test/channelTelegramBriefingTestData";
import { IdentityLinkPanel } from "./IdentityLinkPanel";

describe("IdentityLinkPanel", () => {
  it("shows immediate token result and masked identities", async () => {
    const create = vi.fn();
    render(
      <IdentityLinkPanel
        identities={channelDashboard.linked_identities}
        tokenResult={linkTokenResult}
        onCreateToken={create}
      />,
    );

    expect(screen.getByText("pair-code-10-qa036")).toBeInTheDocument();
    expect(screen.getByText("Telegram user tg-***-1842")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Create Code" }));
    expect(create).toHaveBeenCalledOnce();
  });
});
