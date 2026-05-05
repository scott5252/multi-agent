import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  channelDashboard,
  channelMutation,
  linkTokenResult,
} from "../../test/channelTelegramBriefingTestData";
import { ChannelTelegramBriefingPage } from "./ChannelTelegramBriefingPage";

describe("ChannelTelegramBriefingPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads dashboard and runs safe mutations", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ ok: true, json: async () => channelDashboard })
        .mockResolvedValueOnce({ ok: true, json: async () => channelMutation })
        .mockResolvedValueOnce({ ok: true, json: async () => linkTokenResult }),
    );

    render(<ChannelTelegramBriefingPage channelsUrl="/admin/app/channels/bootstrap.json" />);

    await screen.findByRole("heading", {
      name: "Channel, Telegram, and Briefing Preferences",
    });
    expect(screen.getAllByText("Morning briefing")[0]).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Validate Acme" }));
    await waitFor(() => {
      expect(screen.getAllByText(channelMutation.summary)[0]).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Create Code" }));
    await waitFor(() => {
      expect(screen.getByText("pair-code-10-qa036")).toBeInTheDocument();
    });
    expect(screen.queryByText(/qa036-secret-value|private message/i)).not.toBeInTheDocument();
  });
});
