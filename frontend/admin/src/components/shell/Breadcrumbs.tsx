import type { ReactAdminBreadcrumb } from "../../api/generated/reactAdminApi";

export function Breadcrumbs({ items }: { items: ReactAdminBreadcrumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="breadcrumbs">
      <ol>
        {items.map((item) => (
          <li key={`${item.label}-${item.href ?? "current"}`}>
            {item.href && !item.active ? <a href={item.href}>{item.label}</a> : <span>{item.label}</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}
