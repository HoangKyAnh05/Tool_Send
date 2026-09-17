# 0028 Authoritative Invariant Encoding

Date: 2026-08-11

## Status

Accepted.

## Context

Harness already requires repository authority before externally observable
policy changes. It did not give fresh consumers a direct route for turning an
accepted architecture, reliability, security, or quality boundary into a
mechanical check. It also did not ask onboarding to compare documented
invariants with executable validation.

Without that route, agents may leave accepted rules as prose, invent policy from
conventions, add a parallel validation framework, or overstate a local or CI
check as merge enforcement.

## Decision

1. The compact agent entrypoint routes invariant work to one installed pattern.
2. The workflow requires accepted authority first, the repository-native
   validation owner, the smallest mechanical check, actionable diagnostics, and
   both positive and negative proof.
3. Core installs `$encode-invariant`. Its trigger covers requests to enforce
   boundaries, prevent recurrence, add structural guards, or convert accepted
   rules into validation. Matching requests may invoke it implicitly; it cannot
   infer policy from conventions, code patterns, tests, defaults, or
   undocumented preferences.
4. `$onboard-repository` compares accepted invariants with executable checks in
   its read-only proposal pass. It reports unenforced rules and checks lacking
   authority without editing, executing, enabling, or removing guards.
5. Reports distinguish local validation, optional hooks, checked-in CI
   invocation, observed CI results, and external branch protection. None of
   these levels proves another.
6. The guidance remains implementation-neutral. It prescribes no application
   architecture, language, linter, hook, CI provider, merge policy, or branch
   protection and does not mutate external settings.

## Alternatives Considered

1. **Treat tests or conventions as policy.** Rejected because executable and
   observed truth cannot resolve a missing normative choice.
2. **Put the complete method in `AGENTS.md`.** Rejected because every task would
   pay the context cost for specialized invariant work.
3. **Create a universal validator.** Rejected because consumer repositories own
   their languages, tools, validation commands, and enforcement topology.
4. **Make onboarding silently repair gaps.** Rejected because discovery remains
   read-only and cannot grant authority to mutate what it finds.

## Consequences

- Fresh consumers can discover and apply one authority-gated invariant flow.
- Accepted prose can gain recurrence proof without a second validation system.
- Onboarding exposes documentation/check drift while preserving its read-only
  first pass.
- Agents must report unknown external enforcement rather than infer merge
  blocking from checked-in files.
- The core payload and release candidate grow by one pattern and one skill.
