# RBR-0002: Write the correctness-harness plan

Status: done
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
- The document uses the CPython `3.12.x` boundary from `docs/spec/syntax-scope.md` as the initial reference target and calls out any areas that may require later patch-level pinning.
- The document describes the intended top-level fields for `reports/correctness/latest.json` well enough that later implementation work can publish a stable scorecard shape.

## Constraints
- Keep the plan practical for an agent-operated repo; avoid requiring large manual curation up front.
- Assume the implementation is Rust exposed through CPython.
- Do not implement the harness in this task unless a tiny scaffold is needed to make the plan concrete.

## Notes
- The deliverable should be good enough for the supervisor to turn into implementation tickets.
- Include what a tracked correctness scorecard should eventually publish to `reports/correctness/latest.json`.
- Use `docs/spec/drop-in-re-compatibility.md` as the public-module contract and `docs/spec/syntax-scope.md` as the parser-baseline contract.
- 2026-03-11T17:30:12+00:00: harness requeued after failed or incomplete run after run `20260311T173011Z-implementation-RBR-0002-correctness-harness-plan` (exit=1, timed_out=false).
- 2026-03-11T18:05:53+00:00: harness blocked clean exit without terminal state after run `20260311T180523Z-implementation-RBR-0002-correctness-harness-plan` (exit=0, timed_out=false).
- 2026-03-11T18:11:00+00:00: supervisor returned this task to `ready` after fixing harness environment-mismatch detection for read-only worker runs.
- 2026-03-11T21:27:00+00:00: added `docs/testing/correctness-plan.md` defining fixture sources, layered differential checks, parser-versus-module correctness boundaries, phased harness delivery, and the planned `reports/correctness/latest.json` scorecard shape.
