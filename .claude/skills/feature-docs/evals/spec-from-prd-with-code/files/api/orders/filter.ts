export interface OrdersFilter {
  status?: "pending" | "paid" | "shipped" | "cancelled";
  from?: string; // ISO date, inclusive
  to?: string; // ISO date, inclusive
}

// The one place that turns the Orders page filters into a query; the list endpoint uses it.
export function applyFilter(query, filter: OrdersFilter) {
  if (filter.status) query = query.where("status", filter.status);
  if (filter.from) query = query.where("created_at", ">=", filter.from);
  if (filter.to) query = query.where("created_at", "<=", filter.to);
  return query;
}
