import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { validationResultFixture, patternsEnvelopeFixture } from "../../test/patternsTestData";
import { AdminForm } from "./AdminForm";

describe("AdminForm", () => {
  it("maps backend field errors to form controls and reports dirty state", async () => {
    const onChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <AdminForm
        dirty
        errors={{
          sample_name: validationResultFixture.field_errors[0],
        }}
        fields={patternsEnvelopeFixture.data.form.fields}
        onChange={onChange}
        onSubmit={onSubmit}
        submitting={false}
        values={{
          confirmed: false,
          idempotency_key: "sample-idempotency-key",
          outcome: "accepted",
          revision: "sample-revision-current",
          sample_name: "",
        }}
      />,
    );

    expect(screen.getByText("Unsaved changes")).toBeInTheDocument();
    expect(screen.getByText("Enter a sample name.")).toBeInTheDocument();

    await userEvent.type(screen.getByLabelText(/Sample name/), "Preview");
    await userEvent.click(screen.getByRole("button", { name: "Preview result" }));

    expect(onChange).toHaveBeenCalled();
    expect(onSubmit).toHaveBeenCalled();
  });
});
