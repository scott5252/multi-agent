# Contract: Jinja Infrastructure Decommission

## Runtime Scanner Contract

The scanner test suite must fail when runtime source reintroduces:

- `import jinja2`
- `from jinja2`
- `Jinja2Templates`
- `TemplateResponse`
- `workflow_ui_templates`

Runtime scanner scope:

- `src/multi_agent_platform`
- Excludes built React assets under `src/multi_agent_platform/web_admin/static/react/assets`
- Excludes historical spec artifacts and tests that intentionally mention retired symbols as evidence

## File Scanner Contract

The file scanner must fail when any of these exist:

- Files under `src/multi_agent_platform/web_admin/templates`
- Legacy static files:
  - `src/multi_agent_platform/web_admin/static/admin_shell.js`
  - `src/multi_agent_platform/web_admin/static/model_providers.js`
  - `src/multi_agent_platform/web_admin/static/model_skill_config.js`
  - `src/multi_agent_platform/web_admin/static/prompt_runtime.js`
  - `src/multi_agent_platform/web_admin/static/reliability_controls.js`
  - `src/multi_agent_platform/web_admin/static/run_details.js`
  - `src/multi_agent_platform/web_admin/static/run_inspection.js`
  - `src/multi_agent_platform/web_admin/static/workflow_studio.css`
  - `src/multi_agent_platform/web_admin/static/workflow_studio.js`

## Route Compatibility Contract

Representative browser routes must return React HTML, non-Jinja HTML, redirects, or safe problems:

- `/admin`
- `/admin/app`
- `/admin/app/migration`
- `/auth/local-login`
- `/runs`
- `/runs/new`
- `/runs/{run_id}`

## Dependency Contract

`pyproject.toml` and `uv.lock` must not list `jinja2` as a direct project dependency.
