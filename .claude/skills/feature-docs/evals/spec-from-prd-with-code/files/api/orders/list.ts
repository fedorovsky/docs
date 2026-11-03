import { db } from "../db";
import { OrdersFilter, applyFilter } from "./filter";

export const PAGE_SIZE = 50;

// GET /api/orders?status=&from=&to=&page=  (the API gateway times requests out after 30 s)
export async function listOrders(merchantId: string, filter: OrdersFilter, page = 1) {
  const query = applyFilter(db("orders").where({ merchant_id: merchantId }), filter);
  return query.orderBy("created_at", "desc").limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE);
}
