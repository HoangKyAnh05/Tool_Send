# Execution Plan: Repository Protocol Core

Date: 2026-08-10

## Status

Completed.

## Outcome

`repository-harness` has one current product: a small repository protocol plus
the safe `harness` installer/updater. The optional SQLite control plane,
protocol-v1 implementation, reconstruction state, and their release train no
longer live in the main product repository. Release readiness is proved by
fresh installation, fresh-agent repository navigation, and safe update and
recovery behavior. A full consumer application runtime loop remains useful
research, but is not a release gate or a current product claim.

## Context

- The user explicitly authorized the strong simplification on 2026-08-10.
- `docs/decisions/0019-repository-centered-default-workflow.md` established
  Git-native repository authority.
- `docs/decisions/0024-rust-harness-core-maintenance-cli.md` established the
  independent `harness` maintenance product.
- `docs/decisions/0025-latest-release-self-update-and-human-directed-conflicts.md`
  defines the updater's safety and recovery contract.
- Decisions `0022` and `0023` preserved protocol v1 during a compatibility
  runway. This change ends that runway in this repository; Git history and the
  last published compatibility release preserve the former implementation.

## Scope

In scope:

- Remove `harness-cli` from the Rust workspace and source tree.
- Remove SQLite schemas, tracked snapshots and changesets, compatibility
  installers, release workflows, reconstruction scripts, and dependent tests.
- Remove or archive current-tree documentation whose only authority is the
  superseded control plane or migration history.
- Rewrite current product, architecture, test, contribution, release, and
  installation guidance around `harness` alone.
- Replace the application-runtime completion gate with three owned proofs:
  fresh install, fresh-agent navigation/authority behavior, and safe updater
  lifecycle.

Out of scope:

- Creating or publishing an external archive repository.
- Publishing a release, changing GitHub releases, or migrating an external
  Symphony deployment.
- Claiming that Harness can operate arbitrary consumer applications end to end.
- Rewriting the proven `harness` updater architecture without evidence of a
  defect.
- Modifying the user's pre-existing `.gitignore` change.

## Approach

Make one coherent source-tree cut rather than retaining adapters between old
and new ownership. First freeze the exact removal inventory and successor
decision. Remove compatibility implementation and callers together. Then
rewrite the surviving indexes and validation entry point, add the three owned
proof boundaries, and run the complete surviving suite from a deterministic
checkout state.

## Risks And Recovery

- Removing protocol v1 breaks consumers that still download `harness-cli` from
  this repository. Mitigation: decision 0027 explicitly ends support, records
  `harness-cli-v0.1.22` as the last published release, and keeps installation
  and updates from deleting consumer-owned legacy files.
- Broad deletion can remove a test that also protects the core. Mitigation:
  classify tests by observable owner and retain or rewrite mixed core tests
  before deletion.
- Documentation can retain dead links and legacy terminology. Mitigation: run
  link/authority contracts and repository-wide reference searches.
- Recovery before merge is `git switch main`; after merge it is reverting this
  atomic change or restoring the compatibility implementation from the last
  tagged release. No historical rows are rewritten.

## Progress

- [x] Create `refactor/repository-protocol-core` without touching the existing
  `.gitignore` edit.
- [x] Record the successor architecture decision and exact removal inventory.
- [x] Remove compatibility source, state, release, installer, and tests.
- [x] Rewrite current documentation and validation.
- [x] Add or retain the three owned proof boundaries.
- [x] Run focused and full validation.
- [x] Obtain independent stable-candidate review and resolve findings.

## Decisions

- 2026-08-10: Treat the compatibility cut as one integration boundary. Keeping
  a second transitional implementation in this repository would preserve the
  maintenance cost the change is intended to remove.
- 2026-08-10: Git history and the last released artifact preserve historical
  implementation; the current tree will not duplicate it under a `legacy/`
  directory.
- 2026-08-10: Full consumer runtime operation becomes explicitly bounded
  research. Current release claims cover only capabilities owned and tested by
  Harness.
- 2026-08-10: The product owner explicitly selected protocol-v1 EOL instead of
  migration to Symphony. Decision 0027 records the breaking compatibility
  boundary and last published release.

## Validation

- Focused proof: core Rust tests; installer profiles; update conflict,
  rollback, identity, and recovery tests; workflow and task-authority tests.
- Integration proof: fresh install contains only the declared core and a fresh
  agent can navigate authority without a legacy CLI/database prerequisite.
- Repository-required checks: the simplified `scripts/validate-premerge.sh`,
  documentation/reference contracts, `cargo fmt`, `cargo test`, `cargo clippy`,
  shell syntax, PowerShell installer CI contract, and `git diff --check`.

Observed on 2026-08-10:

- `scripts/validate-premerge.sh` passed, including 30 Rust lifecycle tests,
  Clippy, Bash installation, manifest, workflow, documentation, release
  inventory, release identity, and post-merge recovery contracts.
- `cargo metadata --no-deps --format-version 1` listed only `harness`.
- An independent stable-candidate review reran the complete pre-merge contract
  in an isolated copy and found no Rust lifecycle, Bash installer, or release
  workflow regression.
- The review found two documentation consistency defects: decision 0026 still
  described two profiles, and the real-world issue template linked two deleted
  documents. Both were corrected and covered by the documentation contract.
- PowerShell runtime execution was unavailable locally; the Windows pre-merge
  job remains the platform-owned execution proof.

## Result

Protocol v1 is explicitly EOL under decision 0027. The Rust workspace, install
paths, CI, release automation, current documentation, and validation now expose
only the repository protocol and safe `harness` installer/updater. Historical
source remains in Git, while installers and updates preserve pre-existing
consumer-owned legacy files instead of deleting them.
