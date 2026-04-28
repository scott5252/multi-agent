# QA012 UI Guide: Prompt Library And Agent Runtime Profiles

## Goal

Use this guide to test the Spec 012 sprint through the browser UI. A
non-developer reviewer should be able to start from a local browser, sign in,
create prompt and profile records, validate them, publish or activate them,
grant platform records to a tenant, resolve the active profile, and confirm
history and retirement behavior.

This guide is intentionally browser-first. Setup commands are included only so
the UI has a working local server and deterministic tenants.

## What You Will Build

During this pass, you will create these records from the UI:

1. A tenant-scoped prompt for Acme.
2. A platform-scoped prompt that is granted to Acme.
3. A platform-scoped agent runtime profile that references the platform prompt.
4. A tenant-scoped agent runtime profile that overrides the platform fallback.
5. History, grant, resolve, and retire evidence for the prompt/profile flows.

Use only the synthetic values in this guide. Do not paste real customer text,
API keys, provider tokens, authorization headers, or secret values into any
prompt or fixture field.

## Local Setup

If the server is already running for QA012, skip to **Browser Sign-In**.
Otherwise, run these commands from the repository root.

For the cleanest pass, use a fresh `multi_agent_platform_qa012` database. If
you run this guide against a database that already contains QA012 prompts or
profiles, add a short unique suffix to every slug, display name, and agent key
you enter, and use that same agent key throughout the resolve steps. The exact
expected resolution examples below assume no existing active tenant profile for
agent key `planner`.

1. Copy the QA012 environment file.

   ```bash
   cp specs/012-prompt-runtime-profiles/.env.qa012 .env
   ```

   Expected: no output.

   What this proves: the app is using the QA012 local-principal configuration,
   not a production Auth0 or production database configuration.

2. Install dependencies.

   ```bash
   uv sync
   ```

   Expected: dependency installation completes without errors.

3. Start PostgreSQL.

   ```bash
   docker compose up -d postgres
   ```

   Expected: the `postgres` service is running.

4. Create the QA012 database if it does not already exist.

   ```bash
   docker compose exec -T postgres sh -c \
     'psql -U postgres -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '\''multi_agent_platform_qa012'\''" | grep -q 1 || createdb -U postgres multi_agent_platform_qa012'
   ```

   Expected: no output.

5. Apply migrations.

   ```bash
   uv run alembic upgrade head
   ```

   Expected: Alembic finishes successfully.

6. Seed deterministic tenants.

   ```bash
   docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa012 -v ON_ERROR_STOP=1 <<'SQL'
   INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at)
   VALUES
     ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
     ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
   ON CONFLICT (tenant_id) DO UPDATE SET
     slug = EXCLUDED.slug,
     display_name = EXCLUDED.display_name,
     status = EXCLUDED.status,
     updated_at = CURRENT_TIMESTAMP;
   SQL
   ```

   Expected: PostgreSQL reports an insert or upsert result.

7. Start the API server.

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

   Expected: the server listens on `http://127.0.0.1:8000`.

## Test Data Placement

The synthetic tenant ids, principals, prompt JSON, and profile JSON are repeated
inside each section where you use them. This is intentional: reviewers should
not need to scroll back to a shared test-data block while filling forms.

Reference values used throughout the guide:

```text
Acme tenant id: 11111111-1111-1111-1111-111111111111
Globex tenant id: 22222222-2222-2222-2222-222222222222
Acme tenant admin: tenant-admin-acme
Globex tenant admin: tenant-admin-globex
Platform admin: platform-admin
```

## Browser Sign-In

1. Open the local login page.

   ```text
   http://127.0.0.1:8000/auth/local-login?redirect_to=/admin
   ```

2. Select `tenant-admin-acme`.

   Expected: the browser redirects to `/admin`.

   What this proves: browser testing can use the local QA principal cookie
   instead of manual request headers.

3. Confirm the admin shell is visible.

   Expected:

   - The left navigation contains a **Prompt Runtime** group.
   - **Prompt Library** is visible.
   - **Agent Profiles** is visible.
   - The top scope area shows Acme tenant scope or an Acme tenant selector.

4. To switch users later, open:

   ```text
   http://127.0.0.1:8000/auth/local-logout?redirect_to=/auth/local-login
   ```

   Then open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin` and
   choose the next principal.

## Navigation Flow

Use these links through the admin shell while testing.

```text
Prompt Library: http://127.0.0.1:8000/admin/prompt-runtime/prompts
Create Prompt:  http://127.0.0.1:8000/admin/prompt-runtime/prompts/new
Agent Profiles: http://127.0.0.1:8000/admin/prompt-runtime/profiles
Create Profile: http://127.0.0.1:8000/admin/prompt-runtime/profiles/new
Resolve Profile: http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve
```

Expected navigation behavior:

- Prompt Library opens a table with **Display Name**, **Scope**, **Status**,
  **Validation**, and **Actions**.
- Agent Profiles opens a table with **Agent Key**, **Kind**, **Scope**,
  **Validation**, and **Actions**.
- Prompt rows provide **Edit Draft**, **History**, and, after publish,
  **Version** links.
- Profile rows provide **Edit Draft**, **History**, and, after activation,
  **Active Version** links.
- Prompt **Edit Draft** is useful while an active draft exists. After a prompt
  is published, use **Version** and **History** for review unless a new active
  draft has been created.

What this proves: the Spec 012 workflows are discoverable from the shared admin
console, not hidden behind API-only endpoints.

## Build 1: Tenant Prompt Draft, Preview, Publish, And Retire

Use `tenant-admin-acme` for this section.

### Step 1. Open Prompt Library

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts
```

Expected:

- The page title is **Prompt Library**.
- There is a **Create Prompt** action.
- If no prompts exist yet, the table says no prompt lineages are visible.

What this proves: Acme can reach the prompt library list.

### Step 2. Create A Tenant Prompt

Click **Create Prompt**.

Expected URL:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts/new
```

Fill the form exactly:

```text
Scope: Tenant
Tenant ID: 11111111-1111-1111-1111-111111111111
Display Name: QA012 Tenant Planner Prompt
Slug: qa012-tenant-planner-prompt
Purpose: planner
Usage Notes: Browser QA prompt using synthetic fixture data only.
Prompt Content: Plan safe next steps for {{name}}.
Publish Reason: QA012 browser publish evidence
```

Paste this JSON into **Variables**:

```json
[
  {
    "name": "name",
    "purpose": "Recipient used in a synthetic QA preview",
    "required": true,
    "allowed_value_category": "synthetic",
    "safety_classification": "safe_fixture",
    "sample_guidance": "Use a made-up name only.",
    "display_order": 0
  }
]
```

Paste this JSON into **Fixture Values**:

```json
{
  "name": "Ada"
}
```

Expected:

- **Save Draft** is enabled.
- **Validate** is enabled.
- **Preview** is enabled because fixture values are present.
- **Publish** is disabled before validation passes.

What this proves: a reviewer can author a tenant prompt with variables and
fixture data from the server-rendered form.

### Step 3. Save The Draft

Click **Save Draft**.

Expected:

- The browser redirects to an edit URL like:

  ```text
  /admin/prompt-runtime/prompts/<TENANT_PROMPT_LINEAGE_ID>/edit?flash=prompt-saved
  ```

- The form still contains the display name, slug, prompt content, variables
  JSON, and fixture JSON you entered.

Copy the `<TENANT_PROMPT_LINEAGE_ID>` from the URL into your notes.

What this proves: the browser form creates a prompt lineage and persists a
draft revision.

### Step 4. Validate The Draft

On the edit page, click **Validate**.

Expected:

- The browser returns to the edit page.
- The validation panel says:

  ```text
  Status: passed. Blocking: 0.
  ```

- **Publish** is now available if you have not changed the form after
  validation.

What this proves: validation runs from the UI and records publish-ready
evidence against the current saved draft revision.

### Step 5. Preview The Prompt

Click **Preview**.

Expected:

- The browser opens a URL like:

  ```text
  /admin/prompt-runtime/prompts/<TENANT_PROMPT_LINEAGE_ID>/preview?fixture_set_id=default
  ```

- The page shows a safe rendered preview:

  ```text
  Plan safe next steps for Ada.
  ```

- The page shows redaction categories as `None` unless the fixture safety
  policy redacted something.
- There is a **Back to Draft** link.

What this proves: preview uses only the synthetic fixture values from the form
and does not call a model provider or load live run data.

Important: clicking **Preview** saves a new draft revision before rendering the
preview. After previewing, use **Back to Draft** and run **Validate** again
before publishing. This confirms the exact revision being published has fresh
validation.

### Step 6. Re-Validate And Publish

Click **Back to Draft**.

Click **Validate** again.

Expected: the validation panel returns to `Status: passed`.

Click **Publish** without making further edits.

Expected:

- The browser redirects to a version detail page like:

  ```text
  /admin/prompt-runtime/prompts/versions/<TENANT_PROMPT_VERSION_ID>?flash=prompt-published
  ```

- The detail page shows:

  ```text
  Prompt Version
  Lineage
  Version
  Status active
  Template Digest
  ```

Copy the `<TENANT_PROMPT_VERSION_ID>` into your notes. You will use this
version id when creating the tenant profile override later.

What this proves: the UI publishes an immutable prompt version from a freshly
validated draft.

### Step 7. Check Prompt History

Open the history URL using the lineage id from Step 3.

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts/<TENANT_PROMPT_LINEAGE_ID>/history
```

Expected:

- The page shows a timeline of prompt events.
- Events include the current actor, timestamps, recorded outcomes, and reasons
  when reasons were supplied.
- The history does not expose raw credentials, provider tokens, or unrelated
  tenant data.

What this proves: prompt lifecycle actions are auditable from the browser.

Do not retire this tenant prompt yet. It is needed for the tenant profile
override flow.

## Build 2: Platform Prompt Publish And Tenant Grant

Use `platform-admin` for this section.

### Step 1. Switch To Platform Admin

Open:

```text
http://127.0.0.1:8000/auth/local-logout?redirect_to=/auth/local-login
```

Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin`.

Select `platform-admin`.

Expected: the admin shell returns, and the top scope area shows platform scope.

What this proves: platform-level prompt/profile administration uses the
platform admin principal.

### Step 2. Create A Platform Prompt

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts/new
```

Fill the form exactly:

```text
Scope: Platform
Tenant ID: leave blank
Display Name: QA012 Platform Planner Prompt
Slug: qa012-platform-planner-prompt
Purpose: planner
Usage Notes: Browser QA platform prompt granted to Acme only.
Prompt Content: Build a platform plan for {{name}}.
Publish Reason: QA012 platform prompt publish evidence
```

Paste this JSON into **Variables**:

```json
[
  {
    "name": "name",
    "purpose": "Recipient used in a synthetic QA preview",
    "required": true,
    "allowed_value_category": "synthetic",
    "safety_classification": "safe_fixture",
    "sample_guidance": "Use a made-up name only.",
    "display_order": 0
  }
]
```

Paste this JSON into **Fixture Values**:

```json
{
  "name": "Ada"
}
```

Click **Save Draft**.

Expected: the browser redirects to
`/admin/prompt-runtime/prompts/<PLATFORM_PROMPT_LINEAGE_ID>/edit`.

Copy the platform prompt lineage id into your notes.

What this proves: platform admins can create platform-scoped prompts from the
same UI form.

### Step 3. Validate, Preview, Re-Validate, And Publish

On the platform prompt edit page:

1. Click **Validate**.
2. Confirm `Status: passed`.
3. Click **Preview**.
4. Confirm the preview says:

   ```text
   Build a platform plan for Ada.
   ```

5. Click **Back to Draft**.
6. Click **Validate** again.
7. Click **Publish**.

Expected:

- The browser lands on the platform prompt version detail page.
- **Status** is `active`.
- **Template Digest** is present.

Copy the `<PLATFORM_PROMPT_VERSION_ID>` from the detail page into your notes.
You will paste this id into the platform profile prompt reference JSON.

What this proves: the platform prompt goes through the same save, validation,
preview, and immutable publish workflow as a tenant prompt.

### Step 4. Grant The Platform Prompt To Acme

On the platform prompt version detail page, find the grant form.

Fill:

```text
Tenant IDs to Grant: 11111111-1111-1111-1111-111111111111
Grant Reason: QA012 Acme prompt grant evidence
```

Click **Grant**.

Expected:

- The browser returns to the same prompt version detail page.
- The **Active Grants** list includes:

  ```text
  11111111-1111-1111-1111-111111111111 (active)
  ```

What this proves: a platform prompt version is not tenant-usable until a
platform admin grants that exact immutable version to the tenant.

## Build 3: Platform Agent Profile Activation And Tenant Grant

Use `platform-admin` for this section. You will need the platform prompt
version id copied from Build 2 when filling **Prompt References** below.

### Step 1. Open Agent Profiles

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles
```

Expected:

- The page title is **Agent Profiles**.
- There is a **Create Profile** action.
- There is a **Resolve** action.

What this proves: profile management is available from the Prompt Runtime
navigation group.

### Step 2. Create A Platform Profile Draft

Click **Create Profile**.

Expected URL:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/new
```

Fill the top fields:

```text
Scope: Platform
Tenant ID: leave blank
Agent Key: planner
Agent Kind: Agent
Display Name: QA012 Platform Planner Profile
Purpose: Plan work with a granted platform prompt.
Activation Reason: QA012 platform profile activation evidence
```

In **Prompt References**, paste this JSON. Replace
`<PLATFORM_PROMPT_VERSION_ID>` with the platform prompt version id copied from
Build 2:

```json
[
  {
    "purpose": "planner",
    "required_purpose": "planner",
    "prompt_version_id": "<PLATFORM_PROMPT_VERSION_ID>",
    "required": true
  }
]
```

Paste this JSON into **Model Routing**:

```json
{
  "provider": "openai",
  "model": "gpt-4.1-mini"
}
```

Paste this JSON into **Memory Policy**:

```json
{
  "scope_mode": "read_only",
  "retention_mode": "run"
}
```

Paste this JSON into **Skills**:

```json
[
  {
    "skill": "planning"
  }
]
```

Paste this JSON into **Tools**:

```json
[
  {
    "category": "read"
  }
]
```

Paste this JSON into **Output Contract**:

```json
{
  "type": "object"
}
```

Paste this JSON into **Tests**:

```json
[
  {
    "suite": "planner-smoke"
  }
]
```

Click **Save Draft**.

Expected:

- The browser redirects to:

  ```text
  /admin/prompt-runtime/profiles/<PLATFORM_PROFILE_ID>/edit?flash=profile-saved
  ```

- The JSON sections remain populated.

Copy the `<PLATFORM_PROFILE_ID>` into your notes.

What this proves: the profile workflow stores the prompt references, model
routing hints, memory policy, skills, tool policy, output contract, and test
requirements from the browser.

### Step 3. Validate The Platform Profile

Click **Validate**.

Expected:

- The validation panel says:

  ```text
  Status: passed. Blocking: 0.
  ```

- **Activate** is available if you have not edited the form after validation.

What this proves: profile activation is blocked until all required policy
sections are present and referenced prompt versions are active and authorized.

### Step 4. Activate The Platform Profile

Click **Activate** without making more edits.

Expected:

- The browser redirects to a profile version detail page like:

  ```text
  /admin/prompt-runtime/profiles/versions/<PLATFORM_PROFILE_VERSION_ID>?flash=profile-activated
  ```

- The detail page shows:

  ```text
  Profile Version
  Runtime Profile
  Agent agent / planner
  Version
  Status active
  ```

Copy the `<PLATFORM_PROFILE_VERSION_ID>` into your notes.

What this proves: a validated profile draft becomes an immutable active profile
version.

### Step 5. Grant The Platform Profile To Acme

On the profile version detail page, fill the grant form:

```text
Tenant IDs to Grant: 11111111-1111-1111-1111-111111111111
Grant Reason: QA012 Acme platform profile fallback evidence
```

Click **Grant**.

Expected:

- The page returns to the same profile version detail.
- **Active Grants** includes:

  ```text
  11111111-1111-1111-1111-111111111111 (active)
  ```

What this proves: a platform profile version becomes available to a tenant only
through an explicit per-version grant.

## Build 4: Resolve The Granted Platform Profile As Acme

Use `tenant-admin-acme` for this section.

### Step 1. Switch Back To Acme

Open:

```text
http://127.0.0.1:8000/auth/local-logout?redirect_to=/auth/local-login
```

Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin`.

Select `tenant-admin-acme`.

Expected: the admin shell shows Acme tenant scope.

### Step 2. Resolve The Planner Profile

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve
```

Fill:

```text
Tenant ID: 11111111-1111-1111-1111-111111111111
Agent Key: planner
Agent Kind: Agent
```

Click **Resolve**.

Expected:

- The resolution panel says:

  ```text
  Resolved to <PLATFORM_PROFILE_VERSION_ID> from platform scope.
  ```

- The considered version list includes the platform profile version id.

What this proves: Acme can resolve the granted platform profile as a fallback
when no tenant-specific active profile exists for the same agent key.

## Build 5: Tenant Profile Override And Resolution Priority

Use `tenant-admin-acme` for this section. You will need the tenant prompt
version id copied from Build 1 when filling **Prompt References** below.

### Step 1. Create A Tenant Profile Draft

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/new
```

Fill:

```text
Scope: Tenant
Tenant ID: 11111111-1111-1111-1111-111111111111
Agent Key: planner
Agent Kind: Agent
Display Name: QA012 Tenant Planner Profile
Purpose: Tenant override for planner.
Activation Reason: QA012 tenant profile override evidence
```

In **Prompt References**, paste this JSON. Replace
`<TENANT_PROMPT_VERSION_ID>` with the tenant prompt version id copied from
Build 1:

```json
[
  {
    "purpose": "planner",
    "required_purpose": "planner",
    "prompt_version_id": "<TENANT_PROMPT_VERSION_ID>",
    "required": true
  }
]
```

Paste this JSON into **Model Routing**:

```json
{
  "provider": "openai",
  "model": "gpt-4.1-mini"
}
```

Paste this JSON into **Memory Policy**:

```json
{
  "scope_mode": "read_only",
  "retention_mode": "run"
}
```

Paste this JSON into **Skills**:

```json
[
  {
    "skill": "planning"
  }
]
```

Paste this JSON into **Tools**:

```json
[
  {
    "category": "read"
  }
]
```

Paste this JSON into **Output Contract**:

```json
{
  "type": "object"
}
```

Paste this JSON into **Tests**:

```json
[
  {
    "suite": "planner-smoke"
  }
]
```

Click **Save Draft**.

Expected: the browser redirects to the tenant profile edit page.

Copy the `<TENANT_PROFILE_ID>` from the URL.

What this proves: tenant admins can create tenant-scoped profiles in their own
tenant.

### Step 2. Validate And Activate The Tenant Profile

Click **Validate**.

Expected: the validation panel says `Status: passed`.

Click **Activate** without making further edits.

Expected:

- The browser opens a profile version detail page.
- **Status** is `active`.

Copy the `<TENANT_PROFILE_VERSION_ID>` from the page.

What this proves: tenant-specific profiles can become active when they
reference an active prompt in the same tenant.

### Step 3. Resolve Again

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve?tenant_id=11111111-1111-1111-1111-111111111111&agent_key=planner&agent_kind=agent
```

Expected:

- The resolution panel says:

  ```text
  Resolved to <TENANT_PROFILE_VERSION_ID> from tenant scope.
  ```

What this proves: tenant-scoped active profiles win before granted platform
fallback profiles for the same tenant, agent key, and agent kind.

## Build 6: History And Retirement

This section confirms that records can be stopped for future use without
destroying review evidence.

### Step 1. Review Profile History

Open the tenant profile history URL:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/<TENANT_PROFILE_ID>/history
```

Expected:

- The page shows profile save, validation, and activation events.
- Events show actor, timestamp, outcome, and reason when present.

What this proves: profile lifecycle actions are reviewable from the browser.

### Step 2. Retire The Tenant Profile Version

Open the tenant profile version detail page:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/versions/<TENANT_PROFILE_VERSION_ID>
```

Fill:

```text
Retirement Reason: QA012 tenant profile retirement evidence
```

Click **Retire**.

Expected:

- The browser returns to the same profile version detail.
- **Status** is `retired`.

What this proves: retired profile versions remain visible but stop governing
new profile resolution.

### Step 3. Confirm Resolution Falls Back To Platform Again

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/profiles/resolve?tenant_id=11111111-1111-1111-1111-111111111111&agent_key=planner&agent_kind=agent
```

Expected:

- The resolution panel returns to:

  ```text
  Resolved to <PLATFORM_PROFILE_VERSION_ID> from platform scope.
  ```

What this proves: retired tenant profile versions are not selected for new use,
and the granted platform fallback remains available.

### Step 4. Retire The Tenant Prompt Version

Open the tenant prompt version detail page:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts/versions/<TENANT_PROMPT_VERSION_ID>
```

Fill:

```text
Retirement Reason: QA012 tenant prompt retirement evidence
```

Click **Retire**.

Expected:

- The browser returns to the same prompt version detail.
- **Status** is `retired`.
- Prompt history remains available at:

  ```text
  /admin/prompt-runtime/prompts/<TENANT_PROMPT_LINEAGE_ID>/history
  ```

What this proves: retired prompt versions are blocked for new use but remain
available for historical review.

## Negative Checks

Run these checks after the happy-path builds. Restore valid values after each
check if you continue using the same draft.

### Invalid Prompt Variable JSON

Use `tenant-admin-acme`.

Create a throwaway tenant prompt draft first, because the successful prompts in
the happy path have already been published and no longer have active draft edit
pages.

Open:

```text
http://127.0.0.1:8000/admin/prompt-runtime/prompts/new
```

Fill:

```text
Scope: Tenant
Tenant ID: 11111111-1111-1111-1111-111111111111
Display Name: QA012 Negative Prompt
Slug: qa012-negative-prompt
Purpose: planner
Usage Notes: Negative validation check only.
Prompt Content: Negative check for {{name}}.
```

Paste this valid JSON into **Fixture Values**:

```json
{
  "name": "Ada"
}
```

Change **Variables** to:

```json
[
  {
    "name": "name",
    "purpose": "Duplicate one",
    "required": true
  },
  {
    "name": "name",
    "purpose": "Duplicate two",
    "required": true
  }
]
```

Click **Validate**.

Expected:

- The validation panel fails.
- A blocking finding references `duplicate_variable`.
- **Publish** is not available for that failed draft revision.

What this proves: prompt publication is blocked when the variable contract is
unsafe or ambiguous.

### Missing Fixture Value

On the same throwaway prompt draft, restore **Variables** to this valid JSON:

```json
[
  {
    "name": "name",
    "purpose": "Recipient used in a synthetic QA preview",
    "required": true,
    "allowed_value_category": "synthetic",
    "safety_classification": "safe_fixture",
    "sample_guidance": "Use a made-up name only.",
    "display_order": 0
  }
]
```

Change **Fixture Values** to:

```json
{}
```

Click **Validate**.

Expected:

- The validation panel fails.
- A blocking finding references `missing_fixture_value`.

What this proves: required prompt variables must have safe preview fixture
values before publication.

### Missing Profile Policy Section

Open any profile draft edit page. If you want a disposable draft, create a new
tenant profile with these top fields:

```text
Scope: Tenant
Tenant ID: 11111111-1111-1111-1111-111111111111
Agent Key: planner-negative-policy
Agent Kind: Agent
Display Name: QA012 Negative Policy Profile
Purpose: Negative policy-section validation check.
Activation Reason: QA012 negative profile evidence
```

In **Prompt References**, paste this JSON. Replace
`<PLATFORM_PROMPT_VERSION_ID>` with the active platform prompt version id from
Build 2:

```json
[
  {
    "purpose": "planner",
    "required_purpose": "planner",
    "prompt_version_id": "<PLATFORM_PROMPT_VERSION_ID>",
    "required": true
  }
]
```

Change **Model Routing** to:

```json
{}
```

Paste this JSON into **Memory Policy**:

```json
{
  "scope_mode": "read_only",
  "retention_mode": "run"
}
```

Paste this JSON into **Skills**:

```json
[
  {
    "skill": "planning"
  }
]
```

Paste this JSON into **Tools**:

```json
[
  {
    "category": "read"
  }
]
```

Paste this JSON into **Output Contract**:

```json
{
  "type": "object"
}
```

Paste this JSON into **Tests**:

```json
[
  {
    "suite": "planner-smoke"
  }
]
```

Click **Validate**.

Expected:

- The validation panel fails.
- A blocking finding references `missing_model_routing`.
- **Activate** is not available for that failed draft revision.

What this proves: profile activation requires the full policy contract, not
just a prompt reference.

### Retired Prompt In A New Profile

Create a new tenant profile draft and reference the retired tenant prompt
version from Build 6. Use these top fields:

```text
Scope: Tenant
Tenant ID: 11111111-1111-1111-1111-111111111111
Agent Key: retired-prompt-check
Agent Kind: Agent
Display Name: QA012 Retired Prompt Profile
Purpose: Confirm retired prompts cannot back new profiles.
Activation Reason: QA012 retired prompt negative evidence
```

In **Prompt References**, paste this JSON. Replace
`<TENANT_PROMPT_VERSION_ID>` with the retired tenant prompt version id from
Build 6:

```json
[
  {
    "purpose": "planner",
    "required_purpose": "planner",
    "prompt_version_id": "<TENANT_PROMPT_VERSION_ID>",
    "required": true
  }
]
```

Paste this JSON into **Model Routing**:

```json
{
  "provider": "openai",
  "model": "gpt-4.1-mini"
}
```

Paste this JSON into **Memory Policy**:

```json
{
  "scope_mode": "read_only",
  "retention_mode": "run"
}
```

Paste this JSON into **Skills**:

```json
[
  {
    "skill": "planning"
  }
]
```

Paste this JSON into **Tools**:

```json
[
  {
    "category": "read"
  }
]
```

Paste this JSON into **Output Contract**:

```json
{
  "type": "object"
}
```

Paste this JSON into **Tests**:

```json
[
  {
    "suite": "planner-smoke"
  }
]
```

Click **Validate**.

Expected:

- The validation panel fails.
- A blocking finding references `retired_prompt_blocked`.

What this proves: retired prompt versions cannot be selected for new profile
activation.

### Cross-Tenant URL Access

Use `tenant-admin-globex` for this check.

1. Sign out and sign in as `tenant-admin-globex`.
2. Paste an Acme prompt edit, prompt version, profile edit, or profile version
   URL from your notes.

Expected:

- The request is denied or safely not found.
- The page does not reveal Acme prompt content, profile JSON, history details,
  or tenant-only ids beyond the URL you pasted yourself.

What this proves: tenant-scope enforcement applies to direct browser URLs, not
just list pages.

### Tenant Grant Misuse

Use `tenant-admin-acme` for this check.

Open the tenant prompt version detail page from Build 1 and try to use the
grant form with Acme's tenant id.

Expected:

- The request fails safely with a `grant_not_allowed` style error.
- Tenant prompt versions are not granted because they already belong to one
  tenant; grants are for platform-scoped versions only.

What this proves: grant behavior is restricted to platform prompt/profile
versions.

## Browser Evidence Checklist

Capture screenshots or reviewer notes for these checkpoints:

1. Prompt Library list with the tenant prompt visible to Acme.
2. Prompt edit page after **Save Draft** showing variables and fixture JSON.
3. Prompt validation panel showing `Status: passed`.
4. Prompt preview page showing only the synthetic value `Ada`.
5. Prompt version detail showing `Status active`.
6. Prompt history timeline.
7. Platform prompt version detail showing Acme in **Active Grants**.
8. Agent Profiles list with the platform profile and tenant profile rows.
9. Profile validation panel showing `Status: passed`.
10. Profile version detail showing `Status active`.
11. Platform profile version detail showing Acme in **Active Grants**.
12. Resolve page showing platform fallback before tenant override.
13. Resolve page showing tenant profile after tenant override activation.
14. Retired profile version detail.
15. Retired prompt version detail.
16. Globex direct URL denial or safe not-found behavior.

## Expected Pass Criteria

Mark the UI pass as successful only if all of these are true:

- Prompt and profile workflows are reachable from the admin navigation.
- Save Draft persists browser form input for prompts and profiles.
- Validation runs from the UI and blocks publish or activation on failures.
- Preview renders synthetic fixture data and does not call a model provider.
- Publish creates an immutable active prompt version.
- Activate creates an immutable active profile version.
- Retire changes prompt/profile version status to `retired`.
- Platform grant forms record active tenant grants for platform-scoped versions.
- Tenant profile resolution selects tenant scope before platform fallback.
- Direct cross-tenant URLs do not disclose Acme records to Globex.
- History pages show lifecycle evidence without secrets or unsafe payloads.

## Current UI Notes

- Prompt variables and fixture values are edited as JSON textareas in this
  sprint.
- Profile policy sections are edited as JSON textareas in this sprint.
- **Publish** publishes the latest saved and validated prompt draft revision.
  Do not edit fields after validation unless you save and validate again.
- **Activate** activates the latest saved and validated profile draft revision.
  Do not edit fields after validation unless you save and validate again.
- **Preview** saves a new prompt draft revision before rendering. Re-run
  **Validate** after previewing and before publishing.
- Grant fields accept comma-separated tenant UUIDs.
- Platform grants are per immutable version. Granting one platform version does
  not automatically grant future versions.

## Automated Evidence

After the browser pass, run the focused browser/integration tests and the
standard project gates.

```bash
uv run pytest tests/integration/api/test_prompt_runtime_browser_flows.py tests/integration/api/test_agent_profile_browser_flows.py --no-cov
uv run pytest tests/contract/test_prompt_runtime_profiles_contract.py tests/unit/auth/test_prompt_runtime_policy.py --no-cov
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --no-cov
```

Expected: all commands pass.

What this proves: the manual browser flow is backed by integration tests that
submit the same server-rendered forms, plus contract and policy coverage for
the added API and authorization surfaces.

## Acceptance Evidence Template

```text
Reviewer:
Date:
Browser:

Acme tenant prompt lineage id:
Acme tenant prompt version id:
Platform prompt lineage id:
Platform prompt version id:
Platform profile id:
Platform profile version id:
Tenant profile id:
Tenant profile version id:

Prompt draft saved: Pass / Fail
Prompt validation passed: Pass / Fail
Prompt preview safe: Pass / Fail
Prompt published: Pass / Fail
Platform prompt granted to Acme: Pass / Fail
Platform profile activated: Pass / Fail
Platform profile granted to Acme: Pass / Fail
Platform fallback resolved: Pass / Fail
Tenant override resolved: Pass / Fail
Retirement behavior confirmed: Pass / Fail
Cross-tenant denial confirmed: Pass / Fail
History evidence reviewed: Pass / Fail
Automated evidence passed: Pass / Fail

Notes:
```

## Troubleshooting

If login returns `401`, confirm `.env` was copied from
`specs/012-prompt-runtime-profiles/.env.qa012` and the server was restarted.

If a tenant-scoped save fails, confirm **Tenant ID** is
`11111111-1111-1111-1111-111111111111` while signed in as
`tenant-admin-acme`.

If a platform-scoped save fails, confirm **Tenant ID** is blank and you are
signed in as `platform-admin`.

If **Publish** or **Activate** is disabled, click **Validate** and confirm the
validation panel says `Status: passed`. If you changed the form or clicked
**Preview**, validate again.

If profile validation reports `prompt_version_not_found`, confirm you pasted a
prompt version id from the detail page, not a prompt lineage id from the edit
URL.

If profile validation reports `platform_prompt_grant_required`, confirm the
platform prompt version was granted to Acme before creating a tenant profile
that references it.

If profile resolution does not find the platform fallback, confirm the platform
profile version is active and granted to Acme.

If Globex can see Acme prompt content or profile JSON, stop the QA pass and
report it as a tenant isolation failure.

## Related Files

- `specs/012-prompt-runtime-profiles/qa012.md`
- `specs/012-prompt-runtime-profiles/.env.qa012`
- `src/multi_agent_platform/api/routers/admin_prompts.py`
- `src/multi_agent_platform/api/routers/admin_agent_profiles.py`
- `src/multi_agent_platform/web_admin/templates/prompts/`
- `src/multi_agent_platform/web_admin/templates/agent_profiles/`
- `tests/integration/api/test_prompt_runtime_browser_flows.py`
- `tests/integration/api/test_agent_profile_browser_flows.py`
