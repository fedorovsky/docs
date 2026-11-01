import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { searchEntities } from "../api/search";
import { track } from "../analytics/track";

export function SearchPage() {
  const [params] = useSearchParams();
  const q = params.get("q") ?? "";
  const { data, isLoading } = useQuery({
    queryKey: ["search", q],
    queryFn: ({ signal }) => searchEntities(q, 50, signal),
    enabled: q.length >= 2,
  });

  if (isLoading) return <p>Searching…</p>;
  if (!data) return null;

  const open = (type: string) => () => track("search_result_opened", { type, source: "search_page" });

  return (
    <div>
      <h1>Results for “{q}”</h1>
      <h2>Orders</h2>
      {data.orders.map((o) => (
        <Link key={o.id} to={`/orders/${o.id}`} onClick={open("order")}>
          {o.id} · {o.customerName} · {o.status} · {o.total}
        </Link>
      ))}
      <h2>Customers</h2>
      {data.customers.map((c) => (
        <Link key={c.id} to={`/customers/${c.id}`} onClick={open("customer")}>
          {c.name} · {c.email}
        </Link>
      ))}
    </div>
  );
}
