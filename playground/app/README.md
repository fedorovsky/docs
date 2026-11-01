# Acme Admin

Internal dashboard used by the support and operations teams to look up orders and customers, issue refunds and manage merchants.

- React 18 + TypeScript, Vite
- Routing: react-router v6, route config in `src/routes.tsx`
- Data: TanStack Query on top of `src/api/client.ts`
- Permissions: `usePermissions()` — every route declares the permission it needs
- Analytics: `track()` in `src/analytics/track.ts`
