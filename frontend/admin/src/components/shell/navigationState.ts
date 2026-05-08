import type { ReactAdminNavigationItem } from "../../api/generated/reactAdminApi";

const sectionedParentPaths = new Set(["/admin/app/governance", "/admin/app/skills"]);

export function isNavigationItemActive(item: ReactAdminNavigationItem): boolean {
  if (typeof window === "undefined") {
    return item.active;
  }

  try {
    const current = new URL(window.location.href);
    const target = new URL(item.href, current.origin);
    const targetPanel = target.searchParams.get("panel");
    const currentPanel = current.searchParams.get("panel");

    if (target.pathname === "/admin") {
      return current.pathname === "/admin";
    }

    if (target.pathname === current.pathname) {
      if (targetPanel || currentPanel) {
        return targetPanel === currentPanel;
      }
      return true;
    }

    if (
      current.pathname.startsWith(`${target.pathname}/`) &&
      !targetPanel &&
      !sectionedParentPaths.has(target.pathname)
    ) {
      return true;
    }
  } catch {
    return item.active;
  }

  return false;
}
