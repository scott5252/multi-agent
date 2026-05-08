import { Activity, LogOut, Menu, UserRound, X } from "lucide-react";

import type {
  ReactAdminBootstrap,
  ReactAdminBreadcrumb,
} from "../../api/generated/reactAdminApi";
import { IconButton, ToastRegion } from "../primitives";
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
  const pageTitle = currentPageTitle(bootstrap);
  const breadcrumbs = currentBreadcrumbs(bootstrap, pageTitle);
  const userLabel =
    bootstrap.principal.display_name ?? bootstrap.principal.principal_id;
  const logoutAction = bootstrap.shell.page_actions.find(
    (action) => action.action_id === "log-off",
  );

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
          <Breadcrumbs items={breadcrumbs} />
          <h1>{pageTitle}</h1>
          <p>{bootstrap.shell.product_name}</p>
        </div>
      </div>
      <div className="topbar-side">
        <section className="topbar-fact" aria-label="Signed-in user">
          <UserRound aria-hidden="true" size={17} />
          <span>
            <span className="label">Signed in</span>
            <strong>{userLabel}</strong>
          </span>
        </section>
        <section
          className={`topbar-fact system-health ${bootstrap.system_health.status}`}
          aria-label="System health"
          title={bootstrap.system_health.summary}
        >
          <Activity aria-hidden="true" size={17} />
          <span>
            <span className="label">System health</span>
            <strong>{bootstrap.system_health.label}</strong>
          </span>
        </section>
        <ScopeSwitcher bootstrap={bootstrap} />
        {logoutAction?.href ? (
          <a className="logout-link" href={logoutAction.href}>
            <LogOut aria-hidden="true" size={17} />
            {logoutAction.label}
          </a>
        ) : null}
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

function currentBreadcrumbs(
  bootstrap: ReactAdminBootstrap,
  pageTitle: string,
): ReactAdminBreadcrumb[] {
  if (pageTitle === "Console Home") {
    return [{ label: "Console Home", href: null, active: true }];
  }
  const homeHref =
    bootstrap.navigation
      .flatMap((group) => group.items)
      .find((item) => item.item_id === "home")?.href ?? "/admin/app";
  return [
    { label: "Console Home", href: homeHref, active: false },
    { label: pageTitle, href: null, active: true },
  ];
}

function currentPageTitle(bootstrap: ReactAdminBootstrap): string {
  const currentPath = window.location.pathname;
  if (currentPath === "/admin/app") {
    return "Console Home";
  }

  const matchedItem = bootstrap.navigation
    .flatMap((group) => group.items)
    .filter((item) => {
      const path = pathFromHref(item.href);
      return currentPath === path || currentPath.startsWith(`${path}/`);
    })
    .sort(
      (left, right) =>
        pathFromHref(right.href).length - pathFromHref(left.href).length,
    )[0];

  if (matchedItem) {
    return matchedItem.label;
  }

  return (
    bootstrap.shell.breadcrumbs.find((breadcrumb) => breadcrumb.active)?.label ??
    "Admin"
  );
}

function pathFromHref(href: string): string {
  try {
    return new URL(href, window.location.origin).pathname;
  } catch {
    return href.split("?")[0] || href;
  }
}
