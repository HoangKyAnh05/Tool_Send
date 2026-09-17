# Execution Plan: P1 Invariant Encoding

Date: 2026-08-11

## Status

Completed

## Outcome

A clean consumer installed from this branch receives the complete, generic P1
workflow for discovering accepted invariants and encoding them in repository-
native validation, with coherent source, embedded, and installed inventories.

## Context

- Project-owner directive in the initiating task: accepted scope and product
  authority for P1.
- `AGENTS.md` and `docs/WORKFLOW.md`: repository-first authority and proof gates.
- `docs/ARCHITECTURE.md`: generic installed-core and consumer-ownership boundary.
- Decisions 0020, 0026, and 0028: installed knowledge boundary, explicit
  onboarding, and authoritative invariant encoding.
- `scripts/harness-install-files.txt` and
  `crates/harness/src/infrastructure/embedded_distribution.rs`: canonical and
  embedded payload owners.

## Scope

In scope:

- Compact routing, workflow decision flow, installed invariant pattern, and
  request-triggered encode-invariant skill.
- Read-only onboarding comparison of documented invariants and checks.
- Payload, release classification, documentation map, tests, and clean install
  evidence.

Out of scope:

- Consumer architecture, language, linter, hook, CI-provider, merge-policy, or
  branch-protection prescriptions.
- Installing hooks or mutating external repository settings.
- Push, PR, merge, release publication, or external branch changes.

## Approach

1. Extend existing repository guidance and skills without adding a new control
   plane or enforcement framework.
2. Wire each installed file through the manifest and embedded distribution.
3. Add contract assertions for authority, inventory coherence, release
   classification, installed content, links, and positive/negative behavior.
4. Validate the skill, focused contracts, a clean branch-candidate install, and
   the repository premerge gate.

## Risks And Recovery

- Risk: entrypoint bloat. Keep the managed block below its existing byte and
  combined-context budgets.
- Risk: invented consumer policy. Require accepted documentary authority and
  keep examples implementation-neutral.
- Risk: source/embedded drift. Compare exact inventories and exercise the real
  installer from a clean temporary consumer.
- Recovery: all changes are Git-local; revert this plan's bounded diff if the
  acceptance gate cannot be restored.

## Progress

- [x] Read repository authority, install path, payload owners, and current tests.
- [x] Implement routing, workflow, pattern, skill, and onboarding enhancement.
- [x] Wire source, embedded, release, documentation, and test inventories.
- [x] Run focused validation and fresh-install acceptance.
- [x] Run required premerge validation and record the result.

## Decisions

- 2026-08-11: Use one installed `docs/patterns/encoding-invariants.md` owner for
  detailed guidance; keep `AGENTS.md` as a short route.
- 2026-08-11: Allow `$encode-invariant` to trigger only on matching user requests.
  Decisions 0020 and 0026 make onboarding and audit skills explicit-only, not
  every core skill; installation still invokes no skill.
- 2026-08-11: Keep all writes with Lead because payload source, embedding, and
  integration tests form one moving acceptance scope; use a Peer read-only.

## Validation

- Focused proof: both changed skills passed `quick_validate.py`; authority,
  workflow, docs, release classification, embedded-inventory, and installer
  contracts passed.
- Integration or end-to-end proof: repository-owned Bash install tests built the
  branch candidate, installed clean temporary consumers, found all P1 artifacts,
  resolved every installed local Markdown link, and matched all 26 declared and
  embedded managed paths.
- Independent review: all 23 candidate files reviewed. Accepted findings added
  per-path release classification and full invariant-method contract coverage;
  the stronger test exposed and corrected missing release matching for the
  managed AGENTS block and payload manifest.
- Repository-required checks: `scripts/validate-premerge.sh` passed on
  2026-08-11 after all review corrections.

## Result

The branch candidate installs all P1 artifacts through the repository-owned
path. Source, embedded, and installed inventories agree; installed links
resolve; focused skill and contract checks pass; and the complete premerge gate
passes. No hook, CI setting, merge policy, branch protection, push, PR, merge,
or release publication was performed.
