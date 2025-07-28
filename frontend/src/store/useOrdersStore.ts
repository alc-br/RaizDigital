import { create } from 'zustand';

export interface OrderSummary {
  id: number;
  target_name: string;
  status: string;
  created_at: string;
}

interface OrdersState {
  orders: OrderSummary[];
  setOrders: (orders: OrderSummary[]) => void;
}

export const useOrdersStore = create<OrdersState>((set) => ({
  orders: [],
  setOrders: (orders) => set({ orders }),
}));
