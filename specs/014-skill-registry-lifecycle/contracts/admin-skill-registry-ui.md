# Contract: Admin Skill Registry Web Views

The feature adds server-rendered admin pages under the existing shared admin
shell. Pages use the current Auth0/local-principal authorization, tenant scope
selector, CSRF/session protections, saved filters where applicable, safe empty
states, and redaction helpers.

## `/admin/skill-registry/ui/packages`

Lists platform skill packages visible to the signed-in principal.

**Required controls**:

- Filter by slug, owner, lifecycle state, validation status, tenant
  availability, withdrawal state, quarantine state, and latest semantic
  version.
- Create package action for platform admins only.
- Links to package detail, latest version detail, validation evidence,
  availability management, and audit records when authorized.

**Required safety states**:

- Unauthorized tenant-scoped callers see only tenant-available package
  summaries or a safe not-found response.
- Quarantined packages show blocked install, blocked bind, and blocked runtime
  indicators.
- Unsafe or restricted documentation content is omitted with a redaction
  reason.

## `/admin/skill-registry/ui/packages/{slug}`

Shows a package lineage and safe version summary.

**Required sections**:

- Package identity, owner, approval state, lifecycle state, safe docs summary.
- Published versions with semantic version, manifest digest, artifact digest,
  validation status, availability mode, install counts, withdrawal state, and
  quarantine state.
- Tenant availability grants with actor, timestamp, status, and reason.
- Package-level audit timeline.

**Required controls**:

- Validate/publish candidate version for platform admins.
- Grant/revoke tenant availability for platform admins.
- Withdraw from new installs or quarantine package versions for platform
  admins.

## `/admin/skill-registry/ui/packages/{slug}/versions/{version}`

Shows immutable version provenance.

**Required sections**:

- Manifest summary, approved tool/MCP entrypoint references, tool
  declarations, action categories, network requirements, credential
  requirements, runtime permissions, compatibility metadata, and smoke-test
  fixtures.
- Package artifact, docs, fixtures, manifest digest, content digest, object
  storage provider/key summary, size, media type, and validation evidence.
- Tenant availability grants, install counts, upgrade availability, quarantine
  and runtime block state.

**Required safety states**:

- The page never renders raw package payloads, raw secrets, credential values,
  provider tokens, or unsafe docs/fixtures.
- Unknown or retired approved integration references are blocking findings.

## `/admin/skill-registry/ui/packages/{slug}/candidate`

Guided platform-admin form for candidate validation and publication.

**Required controls**:

- Manifest JSON or upload reference, package artifact reference, safe docs
  reference, fixture bundle reference, validation reason, and idempotency key.
- Inline manifest validation findings by field path.
- Publication confirmation that displays exact semantic version, manifest
  digest, artifact digest, docs digest, fixture digest, and validation run id.

**Conflict behavior**:

- Duplicate semantic versions show a 409-safe error and do not create a
  package version.
- Validation that finds blocking issues does not expose raw payload content.

## `/admin/skill-registry/ui/installations`

Lists tenant skill installations for the selected tenant.

**Required controls**:

- Filter by tenant, slug, semantic version, installation version, readiness,
  credential status, smoke-test status, binding eligibility, quarantine, and
  upgrade availability.
- Install authorized package version.
- Links to credential configuration, smoke-test history, binding preview,
  policy history, upgrade lineage, and audit records.

**Required safety states**:

- Tenant admins see only their tenant's installations.
- Platform admins can filter by tenant but must keep cross-tenant summaries
  separated.
- Blocked readiness rows show actionable findings without exposing secrets.

## `/admin/skill-registry/ui/installations/{installation_id}`

Shows tenant installation detail.

**Required sections**:

- Exact package slug/version, installation version, manifest digest, artifact
  digest, package lifecycle state, availability at install time, upgrade
  lineage, and revision token.
- Credential readiness by manifest requirement, using safe secret-reference or
  delegated-credential summaries only.
- Smoke-test history by fixture, outcome, duration, policy decision summary,
  failure reasons, and evidence artifact link when authorized.
- Binding eligibility with matched Spec 007 policy versions, denied reasons,
  and runtime block/quarantine state.
- Audit timeline scoped to the installation.

**Required controls**:

- Configure credential references.
- Run smoke tests.
- Recompute or promote readiness.
- Preview binding eligibility.
- Install upgrade when a newer authorized package version exists.
- Quarantine or resolve quarantine when authorized.

**Conflict behavior**:

- Credential, smoke-test, readiness, and binding-adjacent actions require the
  current revision token. Stale submissions show a 409 conflict and preserve
  the current state unchanged.

## `/admin/skill-registry/ui/installations/{installation_id}/configure`

Guided tenant-admin form for credential readiness and smoke-test execution.

**Required controls**:

- One control per manifest credential requirement.
- Secret reference picker limited to active, tenant-visible references.
- Delegated credential picker limited to active, unexpired, authorized links.
- Smoke-test fixture selector with required/optional labels.
- Readiness promotion button enabled only when policy prechecks pass.

**Required safety states**:

- Missing, revoked, expired, unauthorized, wrong-scope, and incompatible
  credentials are shown as blocking findings.
- Raw credential entry fields are not present.

## Audit And Export Views

Audit pages reuse existing admin audit patterns and expose safe summaries for
package creation, validation, publication, availability changes, installation,
credential configuration, smoke tests, readiness, binding attempts, upgrades,
withdrawal, quarantine, authorization denials, stale write rejections, and
redactions.

Exports must omit raw package payloads, raw secrets, credential values, unsafe
documentation or fixtures, provider tokens, and cross-tenant data.

## Accessibility And No-JS Behavior

- All mutation forms are usable without JavaScript.
- Validation findings are associated with form fields where possible.
- Buttons and links use existing admin shell styles and accessible labels.
- Tables include clear empty, loading, error, and filtered-no-results states.
