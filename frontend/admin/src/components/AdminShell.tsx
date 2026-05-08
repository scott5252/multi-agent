import type { ReactAdminBootstrap } from "../api/generated/reactAdminApi";
import { ScopeSummary } from "./ScopeSummary";
import { isNavigationItemActive } from "./shell/navigationState";

interface AdminShellProps {
  bootstrap: ReactAdminBootstrap;
}

export function AdminShell({ bootstrap }: AdminShellProps) {
  return (
    <main className="app-frame">
      <aside className="sidebar" aria-label="Admin navigation">
        <a className="brand" href="/admin/app">
          <span>Admin</span>
          <strong>Workspace</strong>
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
                >
                  <span>{item.label}</span>
                  {item.fallback_kind === "jinja" ? <small>Retired link</small> : null}
                </a>
              ))}
            </section>
          ))}
        </nav>
      </aside>
      <section className="content-shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">Admin</p>
            <h1>Console Home</h1>
          </div>
          <a
            className="secondary-link"
            href="/auth/local-logout?redirect_to=/auth/local-login"
          >
            Log off
          </a>
        </header>
        <ScopeSummary bootstrap={bootstrap} />
        <section className="foundation-panel">
          <div>
            <h2>System status</h2>
            <p>
              Current session, health, and contract details for the active admin
              scope.
            </p>
          </div>
          <dl>
            <div>
              <dt>System health</dt>
              <dd>{bootstrap.system_health.label}</dd>
            </div>
            <div>
              <dt>App version</dt>
              <dd>{bootstrap.version.app_version}</dd>
            </div>
            <div>
              <dt>Contract</dt>
              <dd>{bootstrap.version.api_version}</dd>
            </div>
            <div>
              <dt>Assets</dt>
              <dd>{bootstrap.asset_manifest.available ? "Built" : "Unavailable"}</dd>
            </div>
          </dl>
        </section>
      </section>
    </main>
  );
}
