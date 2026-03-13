# RBR-0167: Catch bounded quantified fully-empty conditional benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified fully-empty conditional workflows supported by `RBR-0166` produce real `rebar` timings before alternation-heavy or broader backtracking-heavy empty-arm execution reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_fully_empty_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_fully_empty_boundary` manifest to exercise only the bounded quantified fully-empty workflows already supported by `RBR-0166`, anchored by the current `pattern-fullmatch-numbered-quantified-conditional-group-exists-fully-empty-purged-gap` row and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported workflows, such as `(a(b)?c(?(1)|)){2}` and `(a(?P<word>b)?c(?(word)|)){2}`, while leaving nested conditional composition, empty-yes-arm quantified variants, replacement-conditioned helpers, alternation-heavy repeated arms, deeper nesting, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0166`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0166`.
- Use the existing `pattern-fullmatch-numbered-quantified-conditional-group-exists-fully-empty-purged-gap` row in `benchmarks/workloads/conditional_group_exists_fully_empty_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach quantified fully-empty parity and then leave that newly supported slice absent from benchmark reporting.
