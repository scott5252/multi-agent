Add an agent and workflow test bench for platform and
tenant admins. Admins must be able to create test suites and test cases
with fixture inputs, expected contract shapes, deterministic assertions,
optional evaluator prompts, model/provider mode, tool/skill mode, and
pass/fail thresholds. Admins must run tests against prompt versions, agent
runtime profiles, workflow drafts, published subworkflows, or full
published workflows. Test runs must support safe execution modes: mock
model, mock tools, real model with side effects disabled, and approved
real dependency probes. Test results must show step traces,
model/provider choices, prompt/profile versions, skill versions, token
usage, latency, contract validation results, redacted transcripts,
artifacts, and pass/fail status. Workflow publication may require
selected test suites to pass. Require tenant isolation, safe redaction,
audit records, at least 90 percent coverage, docs, PR notes, testing
instructions, and README updates.