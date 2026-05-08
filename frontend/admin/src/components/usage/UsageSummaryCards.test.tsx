import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { usageDashboard } from "../../test/usageTestData";
import { UsageSummaryCards } from "./UsageSummaryCards";

describe("UsageSummaryCards", () => {
  it("renders cost and confidence summaries without unsafe text", () => {
    render(<UsageSummaryCards cards={usageDashboard.summary_cards} />);

    expect(screen.getByText("Total tokens")).toBeInTheDocument();
    expect(screen.getByText("12,840")).toBeInTheDocument();
    expect(screen.getByText("confirmed")).toBeInTheDocument();
    expect(screen.queryByText(/qa056-secret-value|raw prompt/i)).not.toBeInTheDocument();
  });
});
