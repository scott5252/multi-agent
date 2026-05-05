import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { bootstrapFixture } from "../../test/shellTestData";
import { CommonState, stateByKind } from "./CommonState";

describe("CommonState", () => {
  it("renders safe state copy and actions", () => {
    const state = {
      ...bootstrapFixture.shell.states[1],
      action: {
        action_id: "open-admin",
        label: "Open admin",
        href: "/admin",
        method: "get" as const,
        variant: "secondary" as const,
        disabled_reason: null,
      },
    };

    render(<CommonState state={state} />);

    expect(screen.getByRole("heading", { name: "Partial data" }))
      .toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open admin" })).toHaveAttribute(
      "href",
      "/admin",
    );
  });

  it("falls back when a descriptor is absent", () => {
    expect(stateByKind([], "denied").title).toBe("Admin state unavailable");
  });
});
