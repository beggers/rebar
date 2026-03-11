# RBR-0002: Write the correctness-harness plan

Status: blocked
Owner: implementation
Created: 2026-03-11

## Goal
- Define how `rebar` will prove parser correctness before optimization work begins.

## Deliverables
- `docs/testing/correctness-plan.md`

## Acceptance Criteria
- The document explains fixture sources, differential-testing ideas, and parser-output assertions.
- The document separates parser correctness from later matcher/runtime behavior.
- The document proposes an incremental path from empty repo to automated conformance coverage.

## Constraints
- Keep the plan practical for an agent-operated repo; avoid requiring large manual curation up front.
- Do not implement the harness in this task unless a tiny scaffold is needed to make the plan concrete.

## Notes
- The deliverable should be good enough for the supervisor to turn into implementation tickets.
- 2026-03-11T17:27:15+00:00: harness blocked clean exit without terminal state after run `20260311T172540Z-implementation-RBR-0002-correctness-harness-plan` (exit=0, timed_out=false).
