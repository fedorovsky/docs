import { NavLink } from "react-router-dom";
import { routes } from "../../routes";
import { usePermissions } from "../../auth/usePermissions";

export function Sidebar() {
  const { has } = usePermissions();
  return (
    <nav className="sidebar">
      {routes
        .filter((r) => r.inNav && has(r.permission))
        .map((r) => (
          <NavLink key={r.path} to={r.path}>
            {r.title}
          </NavLink>
        ))}
    </nav>
  );
}
