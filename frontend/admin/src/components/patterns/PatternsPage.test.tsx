import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  patternsEnvelopeFixture,
  validationResultFixture,
} from "../../test/patternsTestData";
import { PatternsPage } from "./PatternsPage";

describe("PatternsPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads the sample envelope and renders reusable data/form patterns", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => patternsEnvelopeFixture,
      }),
    );

    render(<PatternsPage patternsUrl="/admin/app/patterns.json" />);

    await waitFor(() => {
      expect(screen.getByText("Forms and data patterns")).toBeInTheDocument();
    });
    expect(screen.getByText("Workflow readiness review")).toBeInTheDocument();
    expect(screen.getByLabelText(/Sample name/)).toBeInTheDocument();
    expect(screen.getByText("artifact-ref-qa028-tenant")).toBeInTheDocument();
  });

  it("submits sample forms and renders validation feedback", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => patternsEnvelopeFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => validationResultFixture,
        }),
    );

    render(<PatternsPage patternsUrl="/admin/app/patterns.json" />);

    await screen.findByText("Forms and data patterns");
    await userEvent.click(screen.getByRole("button", { name: "Preview result" }));

    await waitFor(() => {
      expect(screen.getByText("validation error")).toBeInTheDocument();
    });
    expect(screen.getByText("Enter a sample name.")).toBeInTheDocument();
  });
});
