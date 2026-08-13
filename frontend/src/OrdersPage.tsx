import { useEffect, useState } from "react";

import { dispatchOrder, listOrders } from "./api";
import type { Order } from "./types";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listOrders()
      .then(setOrders)
      .catch((err: Error) => setError(err.message));
  }, []);

  async function dispatch(id: string) {
    setError(null);

    try {
      const updated = await dispatchOrder(id);
      setOrders((current) =>
        (current ?? []).map((order) => (order.id === id ? updated : order)),
      );
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (orders === null) {
    return (
      <p>{error ? `Could not load orders: ${error}` : "Loading orders…"}</p>
    );
  }

  if (orders.length === 0) return <p>No orders yet.</p>;

  return (
    <section>
      {error && <p>{error}</p>}

      <table>
        <thead>
          <tr>
            <th>Order</th>
            <th>Items</th>
            <th>Total</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id}>
              <td>{order.id}</td>
              <td>
                {order.items
                  .map((item) => `${item.quantity} x ${item.donut_code}`)
                  .join(", ")}
              </td>
              <td>{order.total}</td>
              <td>{order.status}</td>
              <td>
                {order.status === "CREATED" && (
                  <button onClick={() => dispatch(order.id)}>Dispatch</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
