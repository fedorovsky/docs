import type { ReactNode } from "react";
import type { Permission } from "./auth/usePermissions";
import { DashboardPage } from "./pages/DashboardPage";
import { OrdersPage } from "./pages/OrdersPage";
import { OrderDetailsPage } from "./pages/OrderDetailsPage";
import { CustomersPage } from "./pages/CustomersPage";
import { CustomerDetailsPage } from "./pages/CustomerDetailsPage";
import { RefundsPage } from "./pages/RefundsPage";
import { MerchantsPage } from "./pages/MerchantsPage";
import { SearchPage } from "./pages/SearchPage";
import { SettingsPage } from "./pages/SettingsPage";

export interface AppRoute {
  path: string;
  title: string;
  element: ReactNode;
  permission: Permission;
  /** Shown in the sidebar. Detail pages with params are not. */
  inNav: boolean;
}

export const routes: AppRoute[] = [
  { path: "/", title: "Dashboard", element: <DashboardPage />, permission: "dashboard:view", inNav: true },
  { path: "/orders", title: "Orders", element: <OrdersPage />, permission: "orders:view", inNav: true },
  { path: "/orders/:orderId", title: "Order", element: <OrderDetailsPage />, permission: "orders:view", inNav: false },
  { path: "/customers", title: "Customers", element: <CustomersPage />, permission: "customers:view", inNav: true },
  { path: "/customers/:customerId", title: "Customer", element: <CustomerDetailsPage />, permission: "customers:view", inNav: false },
  { path: "/refunds", title: "Refunds", element: <RefundsPage />, permission: "refunds:manage", inNav: true },
  { path: "/merchants", title: "Merchants", element: <MerchantsPage />, permission: "merchants:manage", inNav: true },
  { path: "/search", title: "Search", element: <SearchPage />, permission: "dashboard:view", inNav: false },
  { path: "/settings", title: "Settings", element: <SettingsPage />, permission: "settings:view", inNav: true },
];
