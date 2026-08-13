import { useState } from "react";

import DonutsPage from "./DonutsPage";
import OrderPage from "./OrderPage";
import OrdersPage from "./OrdersPage";

type View = "donuts" | "order" | "orders";

export default function App() {
  const [view, setView] = useState<View>("donuts");

  return (
    <main>
      <h1>Glazr</h1>

      <nav>
        <button onClick={() => setView("donuts")}>Donuts</button>
        <button onClick={() => setView("order")}>Order</button>
        <button onClick={() => setView("orders")}>Orders</button>
      </nav>

      {view === "donuts" && <DonutsPage />}
      {view === "order" && <OrderPage />}
      {view === "orders" && <OrdersPage />}
    </main>
  );
}
