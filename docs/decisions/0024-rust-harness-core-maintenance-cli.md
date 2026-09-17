# 0024 Rust Harness Core Maintenance CLI

Date: 2026-07-21

## Status

Accepted and implemented.

## Context

Copy-on-install could preserve existing files only by skipping them or replacing
them wholesale. It could not safely deliver upstream workflow corrections into
a locally customized repository.

## Decision

The product includes one Rust CLI named `harness`.

It owns:

- initial core installation after platform bootstrap;
- exact installed provenance;
- three-way core updates;
- dry-run and conflict reporting;
- recoverable transactional application;
- status and integrity diagnostics; and
- versioned candidate handoff and executable replacement.

It does not own consumer product behavior, task tracking, work selection,
orchestration, evaluation, or application operation.

Bash and PowerShell are thin platform bootstraps. They download an immutable,
checksum-verified candidate and delegate product semantics to the Rust binary.

## Alternatives Considered

1. **Keep manual copy upgrades.** Rejected because upstream corrections would
   remain fragmented across consumers.
2. **Duplicate update semantics in Bash and PowerShell.** Rejected because
   merge, recovery, provenance, and transaction behavior need one owner.
3. **Create a separately named updater.** Rejected because installation and
   maintenance are one user-facing product.

## Consequences

- Core installation and maintenance have one cross-platform implementation.
- Consumers can receive improvements without silently losing local changes.
- Artifact identity, release publication, conflict UX, and recovery require
  executable proof.
