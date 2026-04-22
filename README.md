# Multi-Agent AI Platform

Production-grade multi-agent AI platform design and delivery workspace for a
Python, FastAPI, LangChain, LangGraph, and PostgreSQL system.

## Mission

- support Web UI, Telegram, and Web API interaction channels
- support reusable agent and subagent workflows with durable parent-child
  lineage
- enforce tenant isolation, fair scheduling, and quota-aware controls
- persist workflow state, approvals, transactions, and immutable memory
- pin in-flight runs to immutable workflow, contract, prompt, model, and
  tool-policy versions
- keep secrets in a secret manager and large artifacts in object storage
- provide auditing, replay, debugging, and admin workflow design surfaces

## Working Agreement

This repository is governed by
[`/.specify/memory/constitution.md`](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
version `1.0.0`, ratified on `2026-04-22`.

All significant work MUST follow the spec-kit flow:

1. `/speckit.constitution` when delivery rules change
2. `/speckit.specify` to define scope and constitution impact
3. `/speckit.plan` to make durability, security, storage, lineage, and
   observability decisions explicit
4. `/speckit.tasks` to create file-specific, test-first work
5. `/speckit.implement` only after the prior artifacts are aligned

## Required Planning Topics

Every approved plan MUST cover:

- constitution check results
- durability, failure recovery, retries, and compensation
- tenant isolation, fairness, and quota controls
- subworkflow boundaries and parent-child lineage
- version-bundle pinning and resume behavior
- secret management, delegated credentials, and tool policy
- artifact storage and retention
- approval, pause, and resume behavior where relevant
- observability, audit, replay, and debugging
- test strategy, documentation tasks, and security review notes

## Repository Guides

- [Constitution](/Users/scottcornell/src/my-projects/multi-agent/.specify/memory/constitution.md)
- [Quickstart](/Users/scottcornell/src/my-projects/multi-agent/docs/quickstart.md)
- [Architecture](/Users/scottcornell/src/my-projects/multi-agent/docs/architecture.md)
- [Spec-Kit Breakdown](/Users/scottcornell/src/my-projects/multi-agent/docs/spec-kit-breakdown.md)
- [Constitution Prompt](/Users/scottcornell/src/my-projects/multi-agent/docs/constitution-prompt.md)
- [Command Prompts](/Users/scottcornell/src/my-projects/multi-agent/.specify/templates/commands)
