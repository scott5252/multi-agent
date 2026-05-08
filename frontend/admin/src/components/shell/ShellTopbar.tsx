import { Menu, X } from "lucide-react";

import type { ReactAdminBootstrap } from "../../api/generated/reactAdminApi";
import { Badge, IconButton, ToastRegion } from "../primitives";
import { Breadcrumbs } from "./Breadcrumbs";
import { ScopeSwitcher } from "./ScopeSwitcher";

export function ShellTopbar({
  bootstrap,
  drawerOpen,
  onMenuClick,
}: {
  bootstrap: ReactAdminBootstrap;
  drawerOpen: boolean;
  onMenuClick: () => void;
}) {
  return (
    <header className="topbar">
      <div className="topbar-main">
        <IconButton
          className="mobile-menu-button"
          icon={drawerOpen ? <X size={18} /> : <Menu size={18} />}
          label={drawerOpen ? "Close navigation" : "Open navigation"}
          onClick={onMenuClick}
          type="button"
          variant="ghost"
        />
        <div>
          <Breadcrumbs items={bootstrap.shell.breadcrumbs} />
          <h1>Admin</h1>
          <p>Shared shell and design system for governed admin work.</p>
        </div>
      </div>
      <div className="topbar-side">
        <ScopeSwitcher bootstrap={bootstrap} />
        <div className="action-row" aria-label="Page actions">
          {bootstrap.shell.page_actions.map((action) =>
            action.href ? (
              <a className={`action-link ${action.variant}`} href={action.href} key={action.action_id}>
                {action.label}
              </a>
            ) : (
              <Badge key={action.action_id} tone="warning">
                {action.label}
              </Badge>
            ),
          )}
        </div>
      </div>
      <ToastRegion
        messages={bootstrap.shell.notifications.map((notification) => ({
          id: notification.notification_id,
          summary: notification.summary,
          title: notification.title,
          tone: notification.tone,
        }))}
      />
    </header>
  );
}
