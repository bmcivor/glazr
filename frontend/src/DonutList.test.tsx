import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import DonutList from "./DonutList";
import type { Donut } from "./types";

const donuts: Donut[] = [
  {
    id: "1",
    donut_code: "CHOCOLATE",
    description: "A chocolatey goodness",
    price: "9.50",
    available: true,
  },
  {
    id: "2",
    donut_code: "STRAWBERRY",
    description: "A strawberry goodness",
    price: "7.50",
    available: true,
  },
];

describe("DonutList", () => {
  it("renders every donut", () => {
    render(<DonutList donuts={donuts} />);

    expect(screen.getByText("CHOCOLATE")).toBeTruthy();
    expect(screen.getByText("STRAWBERRY")).toBeTruthy();
  });

  it("narrows the list when searching", () => {
    render(<DonutList donuts={donuts} />);

    fireEvent.change(screen.getByLabelText("Search donuts"), {
      target: { value: "choc" },
    });

    expect(screen.getByText("CHOCOLATE")).toBeTruthy();
    expect(screen.queryByText("STRAWBERRY")).toBeNull();
  });
});
