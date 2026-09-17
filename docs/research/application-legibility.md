# Application Legibility Research

Status: research, not a release gate.

## Question

Can repository-owned guidance reduce undocumented human intervention when a
fresh agent operates a real consumer application?

The ideal loop is:

```text
discover execution
-> start an isolated instance
-> create deterministic state
-> reproduce through the real interface
-> inspect correlated runtime evidence
-> implement a bounded change
-> run focused proof
-> verify through the same interface
-> clean up only owned resources
```

## Current Evidence

Earlier consumer pilots showed that a small repository authority rule can stop
an agent from inventing rate-limit policy and that explicit onboarding can
surface missing runbook guidance without mutating the consumer.

Those pilots did not prove the complete runtime loop. The detailed transcripts,
intermediate skill revisions, and historical scoring remain available through
Git history.

## Product Boundary

Consumer repositories own runtime commands, dependencies, credentials,
fixtures, readiness, logs, interfaces, state, and cleanup. Harness may adopt a
generic pattern only after repeated consumer evidence shows that it reduces a
real intervention without fabricating policy.

Failure to complete this research does not block a Harness release. Harness
claims only fresh installation, repository navigation and authority behavior,
and safe update/recovery.

## Future Experiment

When a suitable consumer and task exist:

1. Freeze expected behavior and environment prerequisites.
2. Run a clean baseline and record interventions.
3. Improve only consumer-owned guidance.
4. Replay with a fresh agent and the same task and environment.
5. Compare interventions, unsupported claims, interface evidence, and cleanup.
