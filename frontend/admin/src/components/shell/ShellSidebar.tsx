import type { ReactAdminBootstrap } from "../../api/generated/reactAdminApi";
import { isNavigationItemActive } from "./navigationState";

export function ShellSidebar({
  bootstrap,
  onNavigate,
}: {
  bootstrap: ReactAdminBootstrap;
  onNavigate?: () => void;
}) {
  return (
    <aside className="sidebar" aria-label="Admin navigation">
      <a className="brand" href="/admin/app" onClick={onNavigate}>
        <span>{bootstrap.shell.product_name}</span>
        <strong>Admin workspace</strong>
      </a>
      <nav>
        {bootstrap.navigation.map((group) => (
          <section className="nav-group" key={group.label}>
            <h2>{group.label}</h2>
            {group.items.map((item) => (
              <a
                className={isNavigationItemActive(item) ? "nav-item active" : "nav-item"}
                href={item.href}
                key={item.item_id}
                onClick={onNavigate}
              >
                <span>{item.label}</span>
                {item.fallback_kind === "jinja" ? <small>Retired link</small> : null}
              </a>
            ))}
          </section>
        ))}
      </nav>
    </aside>
  );
}
