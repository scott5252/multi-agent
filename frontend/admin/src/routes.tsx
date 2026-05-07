export const disabledRouteFallbacks: Record<string, string> = {};

export const reactPrimaryRoutes = new Set([
  "/admin/app",
  "/admin/app/migration",
  "/admin/app/patterns",
  "/admin/app/operations",
  "/admin/app/workflows",
  "/admin/app/workflows/new",
  "/admin/app/governance",
  "/admin/app/skills",
  "/admin/app/test-bench",
  "/admin/app/memberships",
  "/admin/app/saved-filters",
  "/admin/app/usage",
  "/admin/app/channels",
]);

export function currentDisabledRoute(pathname: string): string | null {
  const prefix = "/admin/app/";
  if (!pathname.startsWith(prefix)) {
    return null;
  }
  const routeKey = pathname.slice(prefix.length).split("/")[0];
  return disabledRouteFallbacks[routeKey] ? routeKey : null;
}
