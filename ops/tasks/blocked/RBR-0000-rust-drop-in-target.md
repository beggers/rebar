# RBR-0000: Define the Rust drop-in `re` target

Status: blocked
Owner: implementation
Created: 2026-03-11

## Goal
- Define the high-level implementation target for `rebar` as a Rust project exposed to CPython as a bug-for-bug compatible replacement for Python's `re` module.

## Deliverables
- `docs/spec/drop-in-re-compatibility.md`

## Acceptance Criteria
- The document explains what "drop-in replacement for `re`" means at the public API boundary.
- The document distinguishes near-term compatibility requirements from explicitly deferred behavior.
- The document explains the expected Rust/CPython integration shape at a high level.
- The document identifies which parts of `re` compatibility must be benchmarked and which must be proven by correctness testing.

## Constraints
- This is a scope and architecture document, not an implementation task.
- Prefer crisp compatibility decisions over exhaustive narrative.
- If a CPython behavior detail is uncertain, call it out explicitly.

## Notes
- This document should anchor later syntax, correctness, and benchmarking work so the project does not drift into "fast parser, wrong module."
- 2026-03-11T18:05:53+00:00: harness blocked clean exit without terminal state after run `20260311T180417Z-implementation-RBR-0000-rust-drop-in-target` (exit=0, timed_out=false).
