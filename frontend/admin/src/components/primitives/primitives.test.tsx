import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
  Badge,
  Button,
  IconButton,
  Panel,
  Tabs,
  TextInput,
} from ".";

describe("design-system primitives", () => {
  it("renders accessible buttons and icon buttons", () => {
    render(
      <>
        <Button variant="primary">Save</Button>
        <IconButton icon={<span aria-hidden="true">x</span>} label="Close" />
      </>,
    );

    expect(screen.getByRole("button", { name: "Save" })).toHaveClass("primary");
    expect(screen.getByRole("button", { name: "Close" })).toBeInTheDocument();
  });

  it("renders badges, panels, tabs, and text inputs with semantic controls", () => {
    const onChange = vi.fn();
    render(
      <Panel>
        <Badge tone="success">Ready</Badge>
        <Tabs
          active="one"
          onChange={onChange}
          tabs={[
            { id: "one", label: "One" },
            { id: "two", label: "Two" },
          ]}
        />
        <TextInput aria-label="Filter" />
      </Panel>,
    );

    expect(screen.getByText("Ready")).toHaveClass("success");
    expect(screen.getByRole("tab", { name: "One" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    expect(screen.getByRole("textbox", { name: "Filter" })).toBeInTheDocument();
  });
});
