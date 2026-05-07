# React UI Contract: No-Jinja Host/Auth/Shell

## Routes

- `/admin/app`: Serves the non-Jinja React host and loads the standard admin shell.
- `/admin/app/*`: Serves the same non-Jinja host for React deep links that are known React routes.
- `/auth/local-login`: Serves a React local-login route in local-principal mode or a safe non-Jinja unavailable/problem response when disabled.
- `/admin`: Redirects to `/admin/app`, preserving safe tenant/query intent.
- `/admin/filters/{admin_area}`: Redirects to React saved-filter management or returns a non-Jinja problem when unsafe.

## React States

- **Host loading**: Shows existing shell loading state while `/admin/app/bootstrap.json` loads.
- **Local login**: Shows enabled local principals, current principal, selected redirect destination, validation errors, and logout link without raw catalog JSON.
- **Saved filters**: Shows list/create/update/delete controls using backend form metadata and mutation results.
- **Denied**: Uses common React state primitives and safe trace id only.
- **Unavailable**: Uses common React state primitives or minimal non-Jinja HTML when bootstrap cannot load.

## Backend-Owned Decisions

- Auth0 redirect, local-principal session creation, logout, redirect sanitization, tenant scope, action tokens, saved-filter authorization, and mutation validation remain server-owned.
- React may render decisions but must not infer authorization, tenant scope, credential readiness, audit outcomes, or deletion safety.

## Redaction Rules

The UI must not render raw secrets, credential values, provider authorization headers, private channel messages, raw prompts/completions, memory contents, raw run payloads, raw tool payloads, raw test transcripts, full Telegram identifiers, link tokens after creation, local filesystem paths, stack traces, or unauthorized tenant labels.
