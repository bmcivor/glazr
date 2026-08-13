export interface Donut {
  id: string;
  donut_code: string;
  description: string;
  price: string;
  available: boolean;
}

export interface OrderItem {
  donut_code: string;
  quantity: number;
  unit_price: string;
}

export interface Order {
  id: string;
  status: "CREATED" | "DISPATCHED";
  created_at: string;
  items: OrderItem[];
  total: string;
}

export interface OrderSelection {
  donut_code: string;
  quantity: number;
}
