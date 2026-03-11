# RBR-0002: Write the correctness-harness plan

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Define how `rebar` will prove parser and public-API correctness before optimization work begins.

## Deliverables
- `docs/testing/correctness-plan.md`

## Acceptance Criteria
- The document explains fixture sources, differential-testing ideas, parser-output assertions, and module-level parity checks.
- The document separates parser correctness from later matcher/runtime behavior while still defining public `re` compatibility checks.
- The document proposes an incremental path from empty repo to automated conformance coverage.
- The document states how the plan will align with the first pinned CPython reference version from `docs/spec/syntax-scope.md`, or names a provisional version boundary if that task has not landed yet.
- The document describes the intended top-level fields for `reports/correctness/latest.json` well enough that later implementation work can publish a stable scorecard shape.

## Constraints
- Keep the plan practical for an agent-operated repo; avoid requiring large manual curation up front.
- Assume the implementation is Rust exposed through CPython.
- Do not implement the harness in this task unless a tiny scaffold is needed to make the plan concrete.

## Notes
- The deliverable should be good enough for the supervisor to turn into implementation tickets.
- Include what a tracked correctness scorecard should eventually publish to `reports/correctness/latest.json`.
- Use `docs/spec/drop-in-re-compatibility.md` as the public-module contract and make any temporary syntax-version assumptions explicit.
- 2026-03-11T17:30:12+00:00: harness requeued after failed or incomplete run after run `20260311T173011Z-implementation-RBR-0002-correctness-harness-plan` (exit=1, timed_out=false).
- 2026-03-11T18:05:53+00:00: harness blocked clean exit without terminal state after run `20260311T180523Z-implementation-RBR-0002-correctness-harness-plan` (exit=0, timed_out=false).
- 2026-03-11T18:11:00+00:00: supervisor returned this task to `ready` after fixing harness environment-mismatch detection for read-only worker runs.
