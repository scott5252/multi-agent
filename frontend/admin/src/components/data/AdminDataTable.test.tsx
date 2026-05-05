import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { patternsEnvelopeFixture } from "../../test/patternsTestData";
import { AdminDataTable } from "./AdminDataTable";

describe("AdminDataTable", () => {
  it("renders safe records, filters, sorting, and export status", () => {
    const onExport = vi.fn();

    render(
      <AdminDataTable
        exportSnapshot={patternsEnvelopeFixture.data.export_snapshot}
        filters={patternsEnvelopeFixture.filters}
        onExport={onExport}
        pagination={patternsEnvelopeFixture.pagination}
        records={patternsEnvelopeFixture.data.records}
        sorting={patternsEnvelopeFixture.sorting}
      />,
    );

    expect(screen.getByText("Workflow readiness review")).toBeInTheDocument();
    expect(screen.getByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("Sorted by Name")).toBeInTheDocument();
    expect(screen.getByText("artifact-ref-qa028-tenant")).toBeInTheDocument();
  });
});
