import { useState } from "react";

import type { Donut } from "./types";

interface Props {
  donuts: Donut[];
}

export default function DonutList({ donuts }: Props) {
  const [search, setSearch] = useState("");

  const term = search.trim().toLowerCase();
  const visible = term
    ? donuts.filter(
        (donut) =>
          donut.donut_code.toLowerCase().includes(term) ||
          donut.description.toLowerCase().includes(term),
      )
    : donuts;

  return (
    <section>
      <input
        aria-label="Search donuts"
        placeholder="Search donuts"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
      />

      {visible.length === 0 ? (
        <p>No donuts match that search.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Description</th>
              <th>Price</th>
              <th>Available</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((donut) => (
              <tr key={donut.id} style={{ opacity: donut.available ? 1 : 0.4 }}>
                <td>{donut.donut_code}</td>
                <td>{donut.description}</td>
                <td>{donut.price}</td>
                <td>{donut.available ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
