# UI Contract: Admin UI Transitional React Label Removal

## Primary Experience

- The admin entry point presents the product as `Admin`.
- Breadcrumbs, navigation, command/search entries, browser title, and shell
  labels avoid transitional implementation wording.
- Domain pages keep domain labels such as workflows, governance, skills,
  memberships, channels, usage, operations, and migration hardening.

## Transitional Label Gate Panel

- Displays a summary with blocked findings, allowed implementation references,
  scanned surfaces, scanned routes, screenshot evidence, and CI status.
- Lists blocking findings first, then allowed implementation references.
- Shows rationale and owner for each allowed implementation reference.
- Does not expose raw secrets, private tenant labels, raw prompts, local
  filesystem paths, or raw payloads.

## Developer-Only Evidence

- Migration evidence may mention React only as implementation context.
- Ordinary navigation and page titles must not use React as a product label.
- QA docs and screenshots must model product terminology.

## Validation Expectations

- Playwright opens `/admin/app` and representative domain pages.
- Playwright captures screenshots that visibly show product-facing terminology.
- Backend route tests verify platform and tenant routes return cleaned labels.
- A post-UI verifier writes a redaction-safe scanner report.
