import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
  migrationDashboard,
  migrationRouteGroups,
} from "../../test/migrationHardeningTestData";
import { MigrationParityMatrix } from "./MigrationParityMatrix";
import { MigrationSummaryHeader } from "./MigrationSummaryHeader";

describe("migration summary and parity matrix", () => {
  it("renders route counts and update metadata", () => {
    render(
      <MigrationSummaryHeader dashboard={migrationDashboard} onRefresh={vi.fn()} />,
    );

    expect(screen.getByRole("heading", { name: "React-only browser UI" })).toBeInTheDocument();
    expect(screen.getByText("Destinations")).toBeInTheDocument();
    expect(screen.getByText("React primary")).toBeInTheDocument();
    expect(screen.getByText("Legacy fallbacks")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Refresh" })).toBeInTheDocument();
  });

  it("renders grouped routes, auth modes, evidence, and redirects", () => {
    render(<MigrationParityMatrix groups={migrationRouteGroups} />);

    const foundation = screen.getByRole("heading", {
      name: "React foundation and shell",
    }).closest("article");
    expect(foundation).not.toBeNull();
    expect(within(foundation as HTMLElement).getByText("qa037-react-home")).toBeInTheDocument();
    expect(screen.getByText("/admin/app")).toBeInTheDocument();
    expect(screen.getByText("/admin/operations")).toBeInTheDocument();
    expect(screen.getByText("qa047-non-jinja-redirect")).toBeInTheDocument();
    expect(screen.getAllByText("auth0-shaped + local-principal").length).toBeGreaterThan(0);
  });
});
