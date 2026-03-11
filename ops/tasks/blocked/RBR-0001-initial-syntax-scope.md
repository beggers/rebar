# RBR-0001: Draft the initial regex syntax scope

Status: blocked
Owner: implementation
Created: 2026-03-11

## Goal
- Produce the first concrete syntax/support map for `rebar` against CPython's regex parser behavior.

## Deliverables
- `docs/spec/syntax-scope.md`

## Acceptance Criteria
- The document lists the major regex construct families that matter for parsing.
- The document distinguishes near-term in-scope behavior from deferred behavior.
- The document explains what "compatible with CPython" means at the parser boundary.

## Constraints
- This is a documentation task. Do not start parser implementation here.
- If you need to make an assumption about CPython behavior, call it out explicitly instead of pretending it is settled.

## Notes
- This document should make later correctness and benchmark work less ambiguous.
- 2026-03-11T17:27:15+00:00: harness blocked clean exit without terminal state after run `20260311T172513Z-implementation-RBR-0001-initial-syntax-scope` (exit=0, timed_out=false).
