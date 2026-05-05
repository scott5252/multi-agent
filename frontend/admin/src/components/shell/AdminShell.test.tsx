import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { bootstrapFixture } from "../../test/shellTestData";
import { AdminShell } from "./AdminShell";

describe("AdminShell", () => {
  it("renders navigation, breadcrumbs, scope, actions, and token metadata", () => {
    render(<AdminShell bootstrap={bootstrapFixture} />);

    expect(screen.getByRole("navigation", { name: "Breadcrumb" })).toHaveTextContent(
      "Admin",
    );
    expect(screen.getByRole("complementary", { name: "Admin navigation" }))
      .toHaveTextContent("Workflow Registry");
    expect(screen.getByLabelText("Admin scope")).toHaveTextContent("Acme");
    expect(screen.getByRole("link", { name: "Existing console" })).toHaveAttribute(
      "href",
      "/admin",
    );
    expect(screen.getAllByText("qa030")).toHaveLength(2);
  });
});
