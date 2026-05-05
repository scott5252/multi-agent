import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { bootstrapFixture } from "../../test/shellTestData";
import { AdminShell } from "./AdminShell";

describe("keyboard and drawer behavior", () => {
  it("opens and closes the mobile navigation control accessibly", () => {
    render(<AdminShell bootstrap={bootstrapFixture} />);

    const button = screen.getByRole("button", { name: "Open navigation" });
    fireEvent.click(button);

    expect(screen.getByRole("button", { name: "Close navigation" }))
      .toBeInTheDocument();
    expect(screen.getAllByRole("complementary", { name: "Admin navigation" }))
      .toHaveLength(2);
  });
});
