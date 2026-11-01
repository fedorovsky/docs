import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { routes } from "./routes";

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: routes.map(({ path, element }) => ({ path, element })),
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
