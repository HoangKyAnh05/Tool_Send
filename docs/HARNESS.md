# Harness Product Model

Harness makes repository truth easier to retrieve and maintain.

## Principles

1. **Repository truth wins.** Product documents, decisions, plans, code, tests,
   CI, runtime evidence, and Git history are authoritative.
2. **Load the smallest useful context.** `AGENTS.md` is an entrypoint, not an
   encyclopedia.
3. **Process follows work shape.** Bounded work stays bounded; coordinated or
   recoverable work gets one durable plan.
4. **Material choices stay human-owned.** Missing product policy stops mutation.
5. **Behavior proves completion.** Workflow records and self-reports do not
   replace executable or observable evidence.
6. **Consumer applications own application operation.** Generic Harness files
   cannot supply stack-specific runtimes, credentials, logs, or fixtures.
7. **Harness maintains only its core.** `harness` safely installs and updates
   managed guidance without becoming a task control plane.

## Installed Core

The core provides:

- a small agent entrypoint;
- workflow and documentation maps;
- product, decision, and execution-plan locations;
- templates for durable work and application operation;
- an invariant-encoding pattern and request-triggered skill; and
- explicit-only onboarding, proposal-audit, and improvement skills.

It provides no fabricated product domains or validation commands.

## Evidence

Release claims are bounded to fresh installation, repository navigation and
authority behavior, and safe updater lifecycle. Consumer runtime experiments
may improve guidance, but they do not become universal capability claims.

## End-Of-Life Boundary

The SQLite control plane and protocol v1 are historical products. They are
available only from immutable historical releases and Git history. The current
tree does not maintain a compatibility implementation, schema, state snapshot,
release train, or installer profile.
