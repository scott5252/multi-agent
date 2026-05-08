# Spec 059 Reviewer Notes

## Summary

Spec 059 removes user-visible transitional implementation labels from the admin
browser UI and adds a protected transitional label gate.

The user-facing product label is now Admin.

The gate reports zero blocked labels and preserves narrow implementation
references for generated identifiers, historical evidence ids, and developer-only
migration context.

## Allowed Implementation References

- `ReactAdmin` generated identifiers are retained for compatibility and are not
  rendered as product labels.
- Historical evidence ids such as `qaNNN-react-*` remain traceable.
- Developer-only migration evidence may describe implementation context when the
  wording is clearly part of the QA gate.

## Terminology Changes

- Admin shell and fallback host copy now use `Admin`.
- Migration hardening visible headings now use `Admin browser UI`.
- Parity matrix labels now say `Admin and legacy destinations`.
- Readiness panels now say `Browser UI readiness`.
- Route and client error messages now use Admin terminology.

## Validation Notes

- Run QA docs validation before spec validation.
- Run `run_spec_qa.py` against the QA059 manifest.
- Run Playwright with process startup to capture both QA059 screenshots.
- Run `scripts/qa/verify_transitional_labels_qa059.py` after Playwright.
- Run `multi-agent-curl-test` after spec-specific validation passes.

## README And Quickstart Impact

No root README update is required for this cleanup because the behavior is
captured in the Spec 059 quickstart and QA docs.

`docs/quickstart.md` does not need a product terminology change for this spec.

## Rollback Guidance

Rollback should redeploy the previous reviewed release only if the Admin shell
cannot render or the scanner reports blocked production-visible labels that
cannot be corrected locally.

Do not roll back database data for this terminology-only spec.

Do not reintroduce fixture data or implementation-era product labels during
rollback.
