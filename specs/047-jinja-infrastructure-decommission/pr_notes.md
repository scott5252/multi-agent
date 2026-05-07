# PR Notes: Jinja Infrastructure Decommission

Spec 047 removes the final server-side template infrastructure after Specs 039 through 046 completed domain parity. The change removes template provider wiring, server-side template files, legacy static files, and the direct jinja2 dependency. The React migration dashboard now presents final React-only decommission evidence, and local login remains a self-contained non-template HTML route.

Validation expectations include runtime import scanners, file scanners, dependency checks, focused backend route tests, frontend migration tests, generated contract checks, full coverage, Spec QA, and Playwright over /admin/app/migration plus /runs.
