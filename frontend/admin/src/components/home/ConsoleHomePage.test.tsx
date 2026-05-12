import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { consoleHomeFixture } from "../../test/consoleHomeTestData";
import { ConsoleHomePage } from "./ConsoleHomePage";

describe("ConsoleHomePage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the workflow onboarding quick action when authorized", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => consoleHomeFixture,
      }),
    );

    render(<ConsoleHomePage homeUrl="/admin/app/home.json" />);

    await waitFor(() => {
      expect(screen.getByRole("link", { name: /Set up workflow/ })).toHaveAttribute(
        "href",
        "/admin/app/workflows/onboarding?tenant_id=11111111-1111-1111-1111-111111111111",
      );
    });
  });
});
