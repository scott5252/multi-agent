# Data Model: Admin UI Transitional React Label Removal

## VisibleTextSurface

- `surface_id`: Stable identifier for the page, route, screenshot, document, or UI state being checked.
- `surface_type`: Shell, navigation, breadcrumb, document title, command result, route response, fallback, redirect, component, screenshot, QA doc, or developer evidence.
- `scope`: Platform, tenant, denied, empty, seeded, or compatibility route context.
- `source_reference`: Route path, component path, document path, or screenshot path.
- `visible_text`: Redaction-safe text summary or matched text excerpt.
- `user_visible`: Whether ordinary users can see the text in production.
- `developer_only`: Whether the surface is bounded to platform reviewer or implementation evidence context.

## TransitionalLabelFinding

- `finding_id`: Stable finding identifier.
- `surface_id`: Visible surface that produced the finding.
- `matched_text`: Redaction-safe matched text.
- `classification`: Blocking transitional label, allowed implementation reference, technical QA context, historical reference, or internal generated identifier.
- `severity`: Blocking, warning, or informational.
- `rationale`: Why the finding is blocking or allowed.
- `owner`: Reviewer or spec owner responsible for the decision.
- `remediation`: Required copy update or allowlist policy note.

## TransitionalLabelGateSummary

- `generated_at`: Report timestamp.
- `blocked_count`: Count of user-visible banned labels.
- `allowed_reference_count`: Count of allowed implementation references.
- `surfaces_scanned`: Count of visible surfaces checked.
- `routes_scanned`: Count of route responses checked.
- `screenshots_checked`: Count of screenshots or Playwright flows used as evidence.
- `ci_status`: Pass, warning, or fail.
- `next_step`: Reviewer-facing instruction.

## QA059EvidenceSet

- `qa_guide`: QA guide path.
- `ui_guide`: UI walkthrough path.
- `user_guide`: Manual QA path.
- `scanner_report`: Verifier report path.
- `playwright_screenshots`: Screenshot paths for admin entry and representative domain pages.
- `curl_artifacts`: Multi-agent curl regression artifact directory.

## State Rules

- Blocking user-visible transitional labels must be removed before validation completes.
- Allowed implementation references require a rationale and owner.
- Developer-only evidence may warn but must not fail the product-facing gate.
- Denied, empty, unavailable, and fallback states are treated as user-visible when returned by production routes.
