import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { channelDashboard } from "../../test/channelTelegramBriefingTestData";
import { BriefingPreferenceAdminPanel } from "./BriefingPreferenceAdminPanel";
import { BriefingPreferenceMutationResultPanel } from "./BriefingPreferenceMutationResultPanel";

describe("BriefingPreferenceAdminPanel", () => {
  it("renders safe import and export evidence controls", async () => {
    const onImport = vi.fn();
    const onExport = vi.fn();
    render(
      <BriefingPreferenceAdminPanel
        evidence={channelDashboard.preference_profiles.import_export_evidence}
        summaries={[
          {
            ...channelDashboard.preference_profiles.current_user_profile!,
            profile_id: "admin-summary",
            principal_label: "Acme user summary",
          },
        ]}
        onExport={onExport}
        onImport={onImport}
      />,
    );

    expect(screen.getByText("preference-artifact-qa036")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Import" }));
    await userEvent.click(screen.getByRole("button", { name: "Export" }));
    expect(onImport).toHaveBeenCalledOnce();
    expect(onExport).toHaveBeenCalledOnce();
  });

  it("renders preference mutation result", () => {
    render(
      <BriefingPreferenceMutationResultPanel
        result={{
          artifact_reference: "preference-export-artifact-qa036",
          audit_reference: "audit-qa036-preference-export",
          field_errors: {},
          next_step: "Use the artifact reference from storage metadata.",
          profile_summary: "Preference export accepted as json.",
          revision: "briefing-pref-rev-qa036-export",
          row_count: 1,
          status: "accepted",
        }}
      />,
    );

    expect(screen.getByText("Preference export accepted as json.")).toBeInTheDocument();
  });
});
