# RBR-0001: Draft the initial regex syntax scope

Status: ready
Owner: implementation
Created: 2026-03-11

## Goal
- Produce the first concrete syntax/support map for `rebar` against CPython's regex parser behavior, in service of a drop-in `re` replacement.

## Deliverables
- `docs/spec/syntax-scope.md`

## Acceptance Criteria
- The document lists the major regex construct families that matter for parsing.
- The document distinguishes near-term in-scope behavior from deferred behavior.
- The document pins the first CPython version or version family that defines the initial compatibility target, or explicitly justifies a narrower reference boundary if a full version pin is still impossible.
- The document explains what "compatible with CPython" means at the parser boundary and how that relates to user-visible `re` behavior.

## Constraints
- This is a documentation task. Do not start parser implementation here.
- Assume the implementation language is Rust and the consumer surface is CPython.
- If you need to make an assumption about CPython behavior, call it out explicitly instead of pretending it is settled.

## Notes
- This document should make later correctness and benchmark work less ambiguous.
- Use `docs/spec/drop-in-re-compatibility.md` as the public-module contract that this syntax document is refining at the parser boundary.
- 2026-03-11T17:30:12+00:00: harness requeued after failed or incomplete run after run `20260311T173011Z-implementation-RBR-0001-initial-syntax-scope` (exit=1, timed_out=false).
- 2026-03-11T18:05:53+00:00: harness blocked clean exit without terminal state after run `20260311T180450Z-implementation-RBR-0001-initial-syntax-scope` (exit=0, timed_out=false).
- 2026-03-11T18:11:00+00:00: supervisor returned this task to `ready` after fixing harness environment-mismatch detection for read-only worker runs.
