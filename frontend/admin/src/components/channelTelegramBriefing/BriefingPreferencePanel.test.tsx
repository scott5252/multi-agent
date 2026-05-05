import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { channelDashboard } from "../../test/channelTelegramBriefingTestData";
import { BriefingPreferencePanel } from "./BriefingPreferencePanel";

describe("BriefingPreferencePanel", () => {
  it("renders complete safe preference profile", async () => {
    const save = vi.fn();
    render(
      <BriefingPreferencePanel
        profile={channelDashboard.preference_profiles.current_user_profile}
        onSave={save}
      />,
    );

    expect(screen.getByText("America/New_York")).toBeInTheDocument();
    expect(screen.getByText("3 masked sender hints")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Save Preferences" }));
    expect(save).toHaveBeenCalledOnce();
  });
});
