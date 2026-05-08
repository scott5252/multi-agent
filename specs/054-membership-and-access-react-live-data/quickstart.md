# Quickstart: Membership And Access React Live Data

## Local Validation

1. Generate updated backend and frontend contracts after schema changes:

   ```bash
   uv run python scripts/frontend/generate_admin_react_types.py
   ```

2. Run focused backend tests:

   ```bash
   uv run pytest --no-cov tests/unit/admin/memberships/test_react_membership_service.py tests/unit/api/test_admin_membership_react_schema.py tests/unit/db/test_membership_repository.py tests/integration/test_admin_react_routes.py -k "membership" -q
   ```

3. Run frontend membership checks:

   ```bash
   npm --prefix frontend/admin test -- --run Membership
   npm --prefix frontend/admin run build
   ```

4. Run scanner and contract checks:

   ```bash
   uv run pytest --no-cov tests/unit/admin/test_live_data_inventory_scanner.py tests/contract/test_admin_react_contract.py -q
   ```

## Required qa054 Validation

1. Validate QA docs:

   ```bash
   bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/054-membership-and-access-react-live-data
   ```

2. Run Spec QA:

   ```bash
   uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml
   ```

3. Run Playwright UI validation:

   ```bash
   uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml --start-processes
   ```

4. Verify the Playwright membership action persisted:

   ```bash
   uv run python scripts/qa/verify_membership_qa054.py
   ```

5. Run the post-spec curl test:

   ```bash
   uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa054-after-spec
   ```

## Expected Evidence

- Empty qa054 membership workspace returns no deterministic QA034 users, invitations, grants, decisions, support overrides, or audits.
- Seeded qa054 membership workspace returns only persisted rows authorized for the active tenant or platform scope.
- Playwright creates or replays an invitation through the UI and captures a screenshot under `output/playwright/qa054_ui/`.
- Post-UI verification reports persisted invitation and audit evidence without raw email, external subject, token, local path, stack trace, or unauthorized tenant label exposure.
