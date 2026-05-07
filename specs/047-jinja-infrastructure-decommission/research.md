# Research: Jinja Infrastructure Decommission

## Decision 1: Remove Template Provider From Container

**Decision**: Delete `build_template_renderer`, the Starlette templating import, and the `workflow_ui_templates` container member.

**Rationale**: Specs 039 through 046 converted browser routes to React hosts, redirects, or non-Jinja HTML. Keeping a template renderer would be dead infrastructure and an accidental reintroduction path.

**Alternatives Considered**:

- Keep the provider unused for rollback: rejected because rollback is redeploying the prior release, and keeping the provider weakens scanner guarantees.
- Replace it with a stub: rejected because source code would still expose a template-rendering abstraction.

## Decision 2: Delete Server Template Directory And Legacy Static Files

**Decision**: Remove `src/multi_agent_platform/web_admin/templates` and legacy files under `web_admin/static` outside `static/react`.

**Rationale**: Domain parity specs already deleted bounded template surfaces. The remaining admin shell templates and legacy JavaScript/CSS files are only useful to retired pages.

**Alternatives Considered**:

- Keep templates as archived reference: rejected because docs/spec artifacts already preserve context and runtime trees should not retain retired assets.
- Keep `workflow_studio.css` for local login: rejected because local login can be self-contained non-Jinja HTML.

## Decision 3: Keep Vite Static Output

**Decision**: Preserve `web_admin/static/react/manifest.json` and built assets.

**Rationale**: React assets are the active browser UI delivery mechanism and are not part of the server-side template runtime.

## Decision 4: Replace Migration Guidance With Final Decommission Evidence

**Decision**: Keep `/admin/app/migration` as a React evidence page, update copy to React-only decommission status, and remove stale retained-fallback guidance.

**Rationale**: The roadmap explicitly treats this page as the operator-facing ledger until Spec 047. In the final state it remains useful as a safe decommission summary.

## Decision 5: Remove Direct `jinja2` Dependency After Scanners Pass

**Decision**: Remove `jinja2>=3.1.0` from `pyproject.toml` and refresh `uv.lock`.

**Rationale**: No runtime source path should import Jinja after container cleanup. Dependency metadata should match runtime behavior.

## Decision 6: Retain Non-Jinja Compatibility Handlers

**Decision**: Keep old browser URL handlers as redirects, aliases, React hosts, or safe problem responses for one release.

**Rationale**: Direct links from bookmarks, notifications, and QA docs must remain safe without server-rendered templates.

## Open Questions

None. All clarification choices use roadmap defaults and local patterns.
