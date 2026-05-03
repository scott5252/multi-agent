Add an operations console for platform administrators.
Platform admins must be able to view system health, dependency readiness,
worker capacity, queue pressure, database pool pressure, object-storage
status, model-provider health, Telegram/channel status, reliability
breaker state, retry/dead-letter state, request latency, run lifecycle
throughput, model latency, token throughput, error rate, and redacted
structured logs. The console must support filtering logs and operational
events by trace id, tenant id, run id, component, severity, status,
dependency, and time range. It must link from operational records to run
inspection, reliability controls, provider connection tests, and usage
dashboards when authorized. It must provide redacted export artifacts and
audit every export or denied access. Tenant admins may receive limited
tenant-scoped operational views only if explicitly included; platform logs
are platform-admin or auditor only. Require safe redaction, retention
awareness, performance tests, at least 90 percent coverage, docs, PR
notes, testing instructions, and README updates.