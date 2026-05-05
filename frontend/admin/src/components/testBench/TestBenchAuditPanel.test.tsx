import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { testBenchAuditFixture } from "../../test/testBenchTestData";
import { TestBenchAuditPanel } from "./TestBenchAuditPanel";

describe("TestBenchAuditPanel", () => {
  it("renders bounded governance evidence", () => {
    render(<TestBenchAuditPanel auditTimeline={[testBenchAuditFixture]} />);

    expect(screen.getByText("Mock mode run launched with idempotency evidence.")).toBeInTheDocument();
    expect(screen.getByText("audit-test-run-launch-qa033")).toBeInTheDocument();
    expect(screen.queryByText(/Globex/)).not.toBeInTheDocument();
  });
});
