import { useEffect, useState } from "react";

import DonutList from "./DonutList";
import { listDonuts } from "./api";
import type { Donut } from "./types";

export default function DonutsPage() {
  const [donuts, setDonuts] = useState<Donut[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDonuts()
      .then(setDonuts)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) return <p>Could not load donuts: {error}</p>;
  if (donuts === null) return <p>Loading donuts…</p>;
  if (donuts.length === 0) return <p>No donuts in the catalogue yet.</p>;

  return <DonutList donuts={donuts} />;
}
