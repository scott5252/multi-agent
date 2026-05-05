import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  governanceDashboardFixture,
  governanceMutationFixture,
} from "../../test/governanceTestData";
import { RoutingPreviewPanel } from "./RoutingPreviewPanel";

describe("RoutingPreviewPanel", () => {
  it("renders ModelGateway-only routing evidence", async () => {
    const onPreview = vi.fn();

    render(
      <RoutingPreviewPanel
        lastResult={{
          ...governanceMutationFixture,
          routing_preview: governanceDashboardFixture.routing_preview,
        }}
        onPreview={onPreview}
        preview={governanceDashboardFixture.routing_preview}
      />,
    );

    expect(screen.getByText("ModelGateway-only execution preserved.")).toBeInTheDocument();
    expect(screen.queryByText(/direct sdk token/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Preview routing/ }));

    expect(onPreview).toHaveBeenCalled();
  });
});
