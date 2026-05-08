import type { ReactNode } from "react";
import { useState } from "react";

import type { ReactAdminBootstrap } from "../../api/generated/reactAdminApi";
import { SavedFilterChips } from "../savedFilters/SavedFilterChips";
import { CommonState } from "../states/CommonState";
import { CommandMenu } from "./CommandMenu";
import { ShellSidebar } from "./ShellSidebar";
import { ShellTopbar } from "./ShellTopbar";

interface AdminShellProps {
  bootstrap: ReactAdminBootstrap;
  children?: ReactNode;
}

export function AdminShell({ bootstrap, children }: AdminShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const partialState = bootstrap.shell.states.find(
    (state) => state.state === "partial_data",
  );

  return (
    <main className="app-frame">
      <div className="desktop-nav">
        <ShellSidebar bootstrap={bootstrap} />
      </div>
      <div className={drawerOpen ? "mobile-nav open" : "mobile-nav"} hidden={!drawerOpen}>
        <ShellSidebar bootstrap={bootstrap} onNavigate={() => setDrawerOpen(false)} />
      </div>
      <section className="content-shell">
        <ShellTopbar
          bootstrap={bootstrap}
          drawerOpen={drawerOpen}
          onMenuClick={() => setDrawerOpen((open) => !open)}
        />
        {children ?? (
          <section className="dashboard-grid" aria-label="Admin shell overview">
            <CommandMenu shell={bootstrap.shell} />
            <SavedFilterChips filters={bootstrap.shell.saved_filters} />
            <section className="foundation-panel">
              <div>
                <p className="eyebrow">Overview</p>
                <h2>System status</h2>
                <p>
                  Current session, health, and contract details for the active
                  admin scope.
                </p>
              </div>
              <dl>
                <div>
                  <dt>System health</dt>
                  <dd>{bootstrap.system_health.label}</dd>
                </div>
                <div>
                  <dt>Principal</dt>
                  <dd>
                    {bootstrap.principal.display_name ??
                      bootstrap.principal.principal_id}
                  </dd>
                </div>
                <div>
                  <dt>Scope</dt>
                  <dd>{bootstrap.active_scope.label}</dd>
                </div>
                <div>
                  <dt>Contract</dt>
                  <dd>{bootstrap.version.api_version}</dd>
                </div>
                <div>
                  <dt>Tokens</dt>
                  <dd>{bootstrap.shell.design_token_version}</dd>
                </div>
              </dl>
            </section>
            {partialState ? <CommonState state={partialState} /> : null}
          </section>
        )}
      </section>
    </main>
  );
}
