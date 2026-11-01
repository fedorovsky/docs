import { api } from "./client";

export interface OrderHit {
  id: string; // e.g. "ORD-10482"
  customerName: string;
  status: "pending" | "paid" | "shipped" | "refunded" | "cancelled";
  total: string;
}

export interface CustomerHit {
  id: string; // e.g. "CUS-2210"
  name: string;
  email: string;
}

export interface SearchResponse {
  orders: OrderHit[];
  customers: CustomerHit[];
}

/**
 * Full-text search across orders (by id) and customers (by id, name, email).
 * Backend: GET /api/search — p95 ≈ 350 ms, min query length 2.
 */
export function searchEntities(q: string, limit = 20, signal?: AbortSignal) {
  const params = new URLSearchParams({ q, limit: String(limit) });
  return api.get<SearchResponse>(`/api/search?${params}`, signal);
}
