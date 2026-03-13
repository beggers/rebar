# RBR-0230: Catch bounded open-ended quantified-alternation benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded open-ended quantified-alternation workflows supported by `RBR-0229` produce real `rebar` timings before broader repeated-backtracking or more structural quantified composition reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `quantified_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0229`, anchored by the existing numbered `pattern.fullmatch` open-ended gap row for `a(b|c){1,}d` and any directly adjacent named, compile, or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported open-ended quantified-alternation workflows while leaving nested alternation, branch-local backreferences, conditional combinations, and broader repeated-backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0229`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0229`.
- Keep this slice in the existing `quantified_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded open-ended quantified-alternation surface.
- This task exists so the queue does not reach bounded open-ended quantified-alternation parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Replaced the old open-ended quantified-alternation known-gap row in `benchmarks/workloads/quantified_alternation_boundary.json` with numbered and named compile/search/fullmatch workloads for the exact `a(b|c){1,}d` and `a(?P<word>b|c){1,}d` slice already supported by `RBR-0229`, including lower-bound and fourth-repetition probes without widening semantics.
- Regenerated `reports/benchmarks/latest.json`; the published combined benchmark scorecard now reports `401` workloads with `365` real `rebar` timings and `36` explicit known gaps, and the quantified-alternation manifest is now fully measured at `42/42`.
- Updated `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py` to assert the republished totals and the new open-ended measured rows, then verified with `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_quantified_alternation_boundary_benchmarks` and a narrow rerun via `PYTHONPATH=python python3 -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.json --report /tmp/rebar_quantified_alt_open_ended.json`.
