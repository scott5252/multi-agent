# Model Skill Routing

Model routing uses deterministic precedence: step override, agent override,
workflow override, then the tenant default. Prompt references resolve
separately with step, agent, then workflow precedence; tenant-global prompts
are invalid so missing prompts fail closed.

Skill bindings, allowed tool policies, outbound domain policies, secret
references, and credential requirements are explicit and cumulative. Missing
skill or tool policy denies access. Outbound destinations are normalized before
matching and rejected when malformed, credential-bearing, or outside the
allowed domain, scheme, or port set.

Runtime provenance records run-level pins and first-use model, prompt, skill,
tool, outbound, secret-reference, and credential decisions. Audit summaries
must contain safe identifiers only, never raw prompts, raw secrets, credential
values, provider tokens, or unauthorized run content.

Reviewers should verify admin APIs, admin web views, rollback history,
migration behavior, and run provenance with:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

