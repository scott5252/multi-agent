# Research: Live Model Credential Resolution For Gateway Calls

## Decision 1: Credential Reference Selection

**Decision**: Use the first configured credential secret reference id in the persisted `credential_secret_reference_ids` list.

**Rationale**: The existing provider connection model already stores references as an ordered list. Preserving order lets administrators express priority without adding new schema or rotation semantics. Using exactly one reference also keeps diagnostics deterministic and avoids silent fallback to stale or overprivileged credentials.

**Alternatives considered**:

- Try all references until one resolves. Rejected because fallback semantics can hide misconfiguration and make audit evidence ambiguous.
- Require exactly one reference. Rejected because the existing model already permits multiple references and future rotation workflows may rely on ordered metadata.
- Select by lexical order. Rejected because lexical order ignores administrator intent.

## Decision 2: OpenAI Requires Credentials

**Decision**: OpenAI provider probes and runtime gateway calls require a configured, resolvable, non-empty credential reference.

**Rationale**: OpenAI-compatible public provider calls need authorization. Failing before the adapter call avoids unnecessary network traffic, avoids provider-side audit noise, and gives operators a deterministic `secret_reference_invalid` category.

**Alternatives considered**:

- Let the adapter call with an empty bearer token. Rejected because it creates misleading authorization failures and does not prove secret resolution.
- Permit direct raw credentials passed to `ModelGateway.invoke`. Rejected for production paths because orchestration state must not carry raw secrets.

## Decision 3: Local OpenAI-Compatible No-Auth Is Allowed Only For Allowlisted Local Endpoints

**Decision**: Local OpenAI-compatible providers may execute without credentials when no reference is configured and the base URL passes the configured local endpoint allowlist. If a reference is configured, it must be resolved at call time and sent as the bearer credential.

**Rationale**: Local QA and developer-hosted model endpoints often run without auth. The existing local endpoint allowlist is the correct guardrail. When admins configure a reference, the behavior must match the feature goal and pass the resolved value into the adapter.

**Alternatives considered**:

- Require credentials for all local providers. Rejected because it breaks existing local/test behavior and is not necessary for allowlisted loopback endpoints.
- Allow no-auth for any URL. Rejected because it bypasses outbound policy guardrails.

## Decision 4: Resolve Per Physical Attempt

**Decision**: Resolve credentials immediately before each provider probe or gateway physical attempt.

**Rationale**: This honors secret rotation and prevents stale resolved values from living in provider records, gateway context, run state, or long-lived service objects.

**Alternatives considered**:

- Resolve on provider save. Rejected because it would persist or cache raw secret values outside the secret provider.
- Resolve once per process. Rejected because rotation and revocation would be delayed and hard to audit.

## Decision 5: Credential Failures Are Provider-Domain Failures

**Decision**: Missing, unresolved, and empty secret values normalize to `secret_reference_invalid` and produce safe probe/gateway evidence without adapter invocation.

**Rationale**: Credential resolution is part of the provider boundary. Operators need one category that points to provider credential configuration without leaking secret details.

**Alternatives considered**:

- Raise uncaught exceptions. Rejected because callers would not get durable provider evidence.
- Map missing credentials to authorization failure. Rejected because no provider authorization decision occurred.

## Decision 6: Safe Evidence Content

**Decision**: Evidence may include reference ids and provider metadata but never raw resolved values, authorization headers, provider request bodies, raw provider response bodies, prompts, completions, or stack traces.

**Rationale**: Reference ids are auditable metadata. Raw values and payloads are high-risk and unnecessary for diagnosis.

**Alternatives considered**:

- Store hashed resolved values. Rejected for this feature because reference ids already provide auditability and hashes can become sensitive correlation artifacts.
- Store provider error bodies after redaction. Rejected because provider error shapes vary and current safe categories are sufficient.

## Decision 7: No Migration Required

**Decision**: Use existing tables and columns.

**Rationale**: `model_provider_connections.credential_secret_reference_ids`, `connection_test_results`, `connection_health_snapshots`, `gateway_invocation_attempts`, `gateway_operations`, and `gateway_physical_attempts` already support the needed metadata and evidence.

**Alternatives considered**:

- Add a credential-resolution attempts table. Rejected as unnecessary for this narrow feature because probe and gateway attempt evidence already anchors the outcome.

## Decision 8: Test-Mode Mocks

**Decision**: Local/CI tests use fake static secret providers and mocked adapters/transports. No real provider calls are required.

**Rationale**: The feature is about resolution boundaries and safe evidence. Real network calls would be unstable and violate the autopilot policy.

**Alternatives considered**:

- Use a real OpenAI test key. Rejected by policy and secret hygiene requirements.
