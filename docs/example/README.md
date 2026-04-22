# Example Subsystems

These examples are small reference implementations that show how the major
subsystems can be shaped in Python.

## Files

- [agent_contracts.py](./agent_contracts.py) - Pydantic contracts for validated
  agent handoffs
- [langgraph_runtime.py](./langgraph_runtime.py) - small LangGraph workflow
  showing controlled orchestration and durable compilation
- [immutable_memory_store.py](./immutable_memory_store.py) - append-only memory
  versioning with head resolution
- [fastapi_auth_toggle.py](./fastapi_auth_toggle.py) - Auth0-enabled production
  auth with a development bypass
- [transactional_outbox.py](./transactional_outbox.py) - transactional outbox
  pattern for durable side effects

## Intended Use

- Use these as design anchors while implementing specs.
- Adapt field names and persistence details to the real repository shape.
- Treat them as subsystem patterns, not final production modules.
