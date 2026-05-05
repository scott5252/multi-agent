import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { bootstrapFixture } from "../../test/shellTestData";
import { CommandMenu } from "./CommandMenu";

describe("CommandMenu", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders authorized local command results", () => {
    render(<CommandMenu shell={bootstrapFixture.shell} />);

    expect(
      screen.getByRole("link", { name: /Workflow Registry/ }),
    ).toHaveAttribute(
      "href",
      "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
    );
  });

  it("fetches safe remote search results when a query is entered", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          query: "workflow",
          results: bootstrapFixture.shell.command_results,
        }),
      }),
    );

    render(<CommandMenu shell={bootstrapFixture.shell} />);
    fireEvent.change(screen.getByLabelText("Search authorized admin destinations"), {
      target: { value: "workflow" },
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });
    expect(
      screen.getByRole("link", { name: /Workflow Registry/ }),
    ).toHaveAttribute(
      "href",
      "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
    );
  });
});
