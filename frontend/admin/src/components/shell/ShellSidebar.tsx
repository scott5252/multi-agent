import { ChevronRight } from "lucide-react";

import type { ReactAdminBootstrap } from "../../api/generated/reactAdminApi";

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
                className={item.active ? "nav-item active" : "nav-item"}
                href={item.href}
                key={item.item_id}
                onClick={onNavigate}
              >
                <span>{item.label}</span>
                <small>
                  {item.fallback_kind === "jinja" ? "Retired link" : "Admin"}
                </small>
                <ChevronRight aria-hidden="true" size={15} />
              </a>
            ))}
          </section>
        ))}
      </nav>
    </aside>
  );
}
