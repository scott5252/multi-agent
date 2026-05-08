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
            <h1>Admin</h1>
          </div>
          <a className="secondary-link" href="/admin">
            Existing console
          </a>
        </header>
        <ScopeSummary bootstrap={bootstrap} />
        <section className="foundation-panel">
          <div>
            <h2>Admin workspaces ready</h2>
            <p>
              Use authorized destinations to manage workflows, operations,
              governance, skills, access, usage, and channels.
            </p>
          </div>
          <dl>
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
