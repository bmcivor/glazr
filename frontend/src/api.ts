import type { Donut, Order, OrderSelection } from "./types";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }

  return (await response.json()) as T;
}

export function listDonuts(search?: string): Promise<Donut[]> {
  const query = search ? `?search=${encodeURIComponent(search)}` : "";
  return request<Donut[]>(`/donuts/${query}`);
}

export function listOrders(): Promise<Order[]> {
  return request<Order[]>("/orders/");
}

export function retrieveOrder(id: string): Promise<Order> {
  return request<Order>(`/orders/${id}/`);
}

export function createOrder(donuts: OrderSelection[]): Promise<Order> {
  return request<Order>("/orders/", {
    method: "POST",
    body: JSON.stringify({ donuts }),
  });
}

export function dispatchOrder(id: string): Promise<Order> {
  return request<Order>(`/orders/${id}/dispatch/`, { method: "POST" });
}
