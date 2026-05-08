import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { governanceDashboardFixture } from "../../test/governanceTestData";
import { PolicyHistoryPanel } from "./PolicyHistoryPanel";
import { ProvenancePanel } from "./ProvenancePanel";

describe("Governance provenance panels", () => {
  it("renders safe policy history and run provenance summaries", () => {
    render(
      <>
        <PolicyHistoryPanel history={governanceDashboardFixture.policy_history} />
        <ProvenancePanel provenance={governanceDashboardFixture.run_provenance} />
      </>,
    );

    expect(screen.getByText("Credential reference metadata was reviewed.")).toBeInTheDocument();
    expect(screen.getByText("1 secret reference(s)")).toBeInTheDocument();
    expect(screen.queryByText(/raw completion/i)).not.toBeInTheDocument();
  });
});
