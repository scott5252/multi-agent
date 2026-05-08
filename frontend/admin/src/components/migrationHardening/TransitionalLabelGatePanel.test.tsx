import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { migrationDashboard } from "../../test/migrationHardeningTestData";
import { TransitionalLabelGatePanel } from "./TransitionalLabelGatePanel";

describe("TransitionalLabelGatePanel", () => {
  it("renders gate summary and allowed implementation context safely", () => {
    render(
      <TransitionalLabelGatePanel gate={migrationDashboard.transitional_label_gate} />,
    );

    expect(screen.getByRole("heading", { name: "Transitional label gate" })).toBeInTheDocument();
    expect(screen.getByText("Admin terminology gate passed for production-visible surfaces.")).toBeInTheDocument();
    expect(screen.getByText("qa059-source-visible-text-scan")).toBeInTheDocument();
    expect(screen.getByText("Generated TypeScript and Python model identifiers keep stable ReactAdmin names for compatibility, but they are not rendered as product labels.")).toBeInTheDocument();
    expect(screen.queryByText("React Admin")).not.toBeInTheDocument();
    expect(screen.queryByText(/qa059-secret-value|raw prompt|\/Users\//i)).not.toBeInTheDocument();
  });

  it("renders unavailable evidence state", () => {
    render(<TransitionalLabelGatePanel gate={null} />);

    expect(screen.getByText("Admin terminology gate evidence is unavailable for this scope.")).toBeInTheDocument();
  });
});
