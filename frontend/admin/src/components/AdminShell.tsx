import type { ReactAdminBootstrap } from "../api/generated/reactAdminApi";
import { ScopeSummary } from "./ScopeSummary";

interface AdminShellProps {
  bootstrap: ReactAdminBootstrap;
}

export function AdminShell({ bootstrap }: AdminShellProps) {
  return (
    <main className="app-frame">
      <aside className="sidebar" aria-label="Admin navigation">
        <a className="brand" href="/admin/app">
          <span>Admin</span>
          <strong>React Foundation</strong>
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
                >
                  <span>{item.label}</span>
                  <small>{item.fallback_kind === "jinja" ? "Existing page" : item.fallback_kind}</small>
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
            <h1>React Admin</h1>
          </div>
          <a className="secondary-link" href="/admin">
            Existing console
          </a>
        </header>
        <ScopeSummary bootstrap={bootstrap} />
        <section className="foundation-panel">
          <div>
            <h2>Foundation ready</h2>
            <p>
              This React shell is authenticated through the existing FastAPI admin service.
              Domain pages remain on their current Jinja routes until their migration specs pass.
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
