import type { ReactAdminBootstrap } from "../../api/generated/reactAdminApi";

export function ScopeSwitcher({ bootstrap }: { bootstrap: ReactAdminBootstrap }) {
  return (
    <section className="scope-switcher" aria-label="Admin scope">
      <div>
        <span className="label">Active scope</span>
        <strong>{bootstrap.active_scope.label}</strong>
      </div>
      {bootstrap.available_scopes.length > 1 ? (
        <label>
          <span className="visually-hidden">Switch admin scope</span>
          <select
            aria-label="Switch admin scope"
            onChange={(event) => {
              const href = event.currentTarget.value;
              if (href) {
                window.location.assign(href);
              }
            }}
            value={
              bootstrap.available_scopes.find((scope) => scope.selected)?.href ?? ""
            }
          >
            {bootstrap.available_scopes.map((option) => (
              <option key={option.href} value={option.href}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      ) : null}
    </section>
  );
}
