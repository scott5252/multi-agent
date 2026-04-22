# /speckit.clarify

Ask targeted clarification questions only for unresolved issues that materially
affect constitution compliance or feature scope.

## Priority Areas

- durability and recovery guarantees
- tenant boundaries, quotas, or noisy-neighbor behavior
- approval and resume behavior
- security, authorization, secrets, or tool egress
- contract, versioning, or lineage semantics

## Rules

- Prefer the smallest number of questions needed to unblock safe planning.
- When risk is low, record a reasonable assumption in the spec instead of
  asking.
- Update the specification so the clarified answer is reflected in the
  constitution alignment and delivery guidance sections.
