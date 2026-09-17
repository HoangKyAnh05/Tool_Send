# 0027 End Protocol V1 And Focus The Repository Protocol

Date: 2026-08-10

## Status

Accepted. Implementation is active on
`refactor/repository-protocol-core`.

## Context

The repository-centered workflow and the independent Rust `harness` updater
are now the product. The optional `harness-cli` still implements the earlier
SQLite lifecycle and machine protocol v1. Keeping that implementation in the
same workspace makes every product change carry its schemas, snapshots,
changesets, release automation, installer profile, historical story packets,
and approximately 18,000 lines of compatibility Rust.

Decisions 0022 and 0023 intentionally retained protocol v1 while Symphony and
explicit CLI users depended on it. That runway achieved a safe separation, but
it also left the current repository maintaining two products with different
sources of truth. On 2026-08-10 the product owner explicitly chose protocol-v1
end of support rather than another cross-repository migration.

The repository release pointer reached `harness-cli-v0.1.23`, but the last
published immutable GitHub release is `harness-cli-v0.1.22`. The published
release and prior Git tags preserve the supported historical implementation;
the unpublished pointer does not define a release that consumers can depend
on.

## Decision

1. Protocol v1 and the optional SQLite control plane are end-of-life.
2. `repository-harness` will build and publish only the `harness` binary.
3. The current tree removes `harness-cli`, schemas, tracked database state,
   changesets, compatibility installers, protocol contracts, compatibility
   release automation, and tests whose only owner was that surface.
4. Historical source remains available through Git history. Existing consumers
   may pin the last published `harness-cli-v0.1.22` release, but it receives no
   new features, fixes, or compatibility guarantee from the current product.
5. Harness installation and updates do not delete a consumer's existing
   `harness-cli` binary, `harness.db`, schemas, or other legacy files. Those
   bytes are consumer-owned after EOL and require an explicit local migration
   or removal decision.
6. The active product claim is limited to a repository protocol and its safe
   installer/updater. Release evidence covers fresh installation,
   repository-navigation and authority behavior, and update/conflict/recovery.
7. A full consumer application runtime loop remains useful research. It is not
   a release gate and is not implied by the phrase “agent-ready repository.”
8. Decisions 0021, 0022, and 0023 are superseded. Their historical rationale
   remains in Git rather than in the current documentation tree.

## Alternatives Considered

1. **Move protocol v1 into Symphony before cleanup.** Rejected by the product
   owner because the protocol is no longer part of the chosen product outcome.
   Symphony may independently adopt or replace its pinned dependency.
2. **Keep `harness-cli` in maintenance mode indefinitely.** Rejected because
   its source, data, release, installer, and validation surfaces continue to
   dominate maintenance even when no features are added.
3. **Move compatibility files under a `legacy/` directory.** Rejected because
   the old commands would remain searchable, buildable, linkable, and subject
   to current-tree maintenance. Git tags already provide an immutable archive.
4. **Require a full consumer runtime experiment before simplifying.** Rejected
   because application runtime, credentials, fixtures, logs, and cleanup are
   consumer-owned. They cannot be an honest release gate for capabilities
   Harness does not own.

## Consequences

Positive:

- The source tree, Rust workspace, installers, CI, and release train represent
  one product.
- Local validation no longer depends on an ignored SQLite database or tracked
  reconstruction state.
- Agents encounter current repository guidance instead of a second historical
  lifecycle.
- Validation claims are limited to behavior the product can reproduce.

Tradeoffs:

- Protocol-v1 consumers receive no post-`v0.1.22` maintenance from this
  repository.
- Symphony installations that need new protocol behavior must own a migration
  or replacement.
- Old databases remain readable only with a pinned historical binary or an
  independently maintained export path.
- This is a breaking product-line decision and requires explicit release notes.

## Verification

- `cargo metadata` lists only the `harness` package.
- Fresh Bash and PowerShell installs expose no compatibility flags, schemas,
  database rules, or `harness-cli` artifact.
- Pre-merge and core release workflows do not install SQLite, bootstrap a
  database, build a compatibility binary, or publish compatibility assets.
- Focused install, navigation/authority, update, conflict, rollback, recovery,
  checksum, and release-identity tests pass.
- Current-tree references to protocol v1 remain only in this EOL decision,
  migration/release notes, and immutable changelog history.
