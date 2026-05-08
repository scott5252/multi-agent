import { beforeEach, describe, expect, it } from "vitest";

import type { ReactAdminNavigationItem } from "../../api/generated/reactAdminApi";
import { isNavigationItemActive } from "./navigationState";

function navItem(href: string): ReactAdminNavigationItem {
  return {
    active: false,
    admin_area: null,
    fallback_kind: "react",
    group: "Test",
    href,
    item_id: href,
    label: href,
    preserve_tenant_scope: true,
    required_scope: "either",
    route_surface_key: "GET:/admin/app",
  };
}

describe("isNavigationItemActive", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/admin/app");
  });

  it("does not mark Console Home active inside the app shell", () => {
    expect(isNavigationItemActive(navItem("/admin"))).toBe(false);
  });

  it("distinguishes sectioned skill subroutes from the skill registry parent", () => {
    window.history.pushState({}, "", "/admin/app/skills/installations");

    expect(isNavigationItemActive(navItem("/admin/app/skills"))).toBe(false);
    expect(isNavigationItemActive(navItem("/admin/app/skills/installations"))).toBe(
      true,
    );
  });

  it("distinguishes panel links that share the channels path", () => {
    window.history.pushState({}, "", "/admin/app/channels?panel=briefing");

    expect(isNavigationItemActive(navItem("/admin/app/channels?panel=telegram"))).toBe(
      false,
    );
    expect(isNavigationItemActive(navItem("/admin/app/channels?panel=briefing"))).toBe(
      true,
    );
  });
});
