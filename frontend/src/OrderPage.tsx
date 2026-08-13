import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { createOrder, listDonuts } from "./api";
import type { Donut, Order } from "./types";

export default function OrderPage() {
  const [donuts, setDonuts] = useState<Donut[]>([]);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    listDonuts()
      .then(setDonuts)
      .catch((err: Error) => setError(err.message));
  }, []);

  const selections = Object.entries(quantities)
    .filter(([, quantity]) => quantity > 0)
    .map(([donut_code, quantity]) => ({ donut_code, quantity }));

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);

    try {
      setOrder(await createOrder(selections));
      setQuantities({});
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={submit}>
      {order && (
        <p>
          Order {order.id} placed. Total {order.total}.
        </p>
      )}
      {error && <p>{error}</p>}

      {donuts
        .filter((donut) => donut.available)
        .map((donut) => (
          <div key={donut.id}>
            <label htmlFor={donut.donut_code}>
              {donut.donut_code} — {donut.price}
            </label>
            <input
              id={donut.donut_code}
              type="number"
              min={0}
              value={quantities[donut.donut_code] ?? 0}
              onChange={(event) =>
                setQuantities({
                  ...quantities,
                  [donut.donut_code]: Number(event.target.value),
                })
              }
            />
          </div>
        ))}

      <button type="submit" disabled={pending || selections.length === 0}>
        Place order
      </button>
    </form>
  );
}
