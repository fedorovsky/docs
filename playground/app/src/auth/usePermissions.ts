import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export type Permission =
  | "dashboard:view"
  | "orders:view"
  | "customers:view"
  | "refunds:manage"
  | "merchants:manage"
  | "settings:view";

interface Me {
  id: string;
  name: string;
  permissions: Permission[];
}

export function usePermissions() {
  const { data } = useQuery({ queryKey: ["me"], queryFn: () => api.get<Me>("/api/me") });
  const granted = new Set(data?.permissions ?? []);
  return { has: (p: Permission) => granted.has(p), loaded: data !== undefined };
}
