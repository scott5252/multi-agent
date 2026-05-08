import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { bootstrapFixture } from "../../test/shellTestData";
import { AdminShell } from "./AdminShell";

describe("AdminShell", () => {
  it("renders navigation, breadcrumbs, session status, scope, and token metadata", () => {
    window.history.pushState({}, "", "/admin/app");

    render(<AdminShell bootstrap={bootstrapFixture} />);

    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toHaveTextContent(
      "Console Home",
    );
    expect(screen.getByRole("complementary", { name: "Admin navigation" }))
      .toHaveTextContent("Workflow Registry");
    expect(screen.getByRole("heading", { name: "Console Home" })).toBeInTheDocument();
    expect(screen.getByLabelText("Signed-in user")).toHaveTextContent("Tenant Admin");
    expect(screen.getByLabelText("System health")).toHaveTextContent("Ready");
    expect(screen.getByLabelText("Admin scope")).toHaveTextContent("Acme");
    expect(screen.getByRole("link", { name: "Log off" })).toHaveAttribute(
      "href",
      "/auth/local-logout?redirect_to=/auth/local-login",
    );
    expect(screen.queryByRole("link", { name: "Workflows" })).not.toBeInTheDocument();
    expect(screen.getAllByText("qa030")).toHaveLength(2);
  });
});
