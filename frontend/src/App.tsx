import { useState } from "react";
import DonutsPage from "./DonutsPage";
type View = "donuts" | "orders";

export default function App() {
  const [view, setView] = useState<View>("donuts");

  return (
    <main>
      <h1>Glazr</h1>

      <nav>
        <button onClick={() => setView("donuts")}>Donuts</button>
        <button onClick={() => setView("orders")}>Orders</button>
      </nav>

      {view === "donuts" ? <DonutsPage /> : <p>orders here</p>}
    </main>
  );
}
