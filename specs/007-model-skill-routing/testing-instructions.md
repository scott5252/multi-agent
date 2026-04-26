# Testing Instructions: Model Skill Routing

Run the quality gate:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Acceptance paths:

- Administrator sets tenant default model and verifies model precedence under 5 minutes for SC-002.
- Administrator adds workflow, agent, and step prompt references and verifies prompt precedence.
- Maintainer binds a skill, allows a tool, denies an outbound domain, and verifies credential failure without side effects.
- Auditor reviews history, rollback records, and run provenance without raw prompts, raw secrets, credential values, or provider tokens.
- Reviewer records elapsed time, tester role, scenario, start timestamp, end timestamp, assisted or unassisted status, completion status, and aggregate pass/fail calculations.
- SC-008 evidence must show at least 90 percent unassisted findability for history and provenance among administrator and maintainer testers.

