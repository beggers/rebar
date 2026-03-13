# RBR-0224: Catch bounded quantified-alternation backtracking-heavy benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified-alternation backtracking-heavy workflows supported by `RBR-0223` produce real `rebar` timings before wider counted ranges, open-ended repeats, or broader repeated-backtracking execution reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `quantified_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0223`, anchored by the existing numbered `pattern.fullmatch` backtracking-heavy gap row for `a(b|bc){1,2}d` and any directly adjacent named or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified-alternation backtracking-heavy workflows while leaving wider counted ranges, open-ended repeats, branch-local backreferences, conditional combinations, and broader repeated-backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0223`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0223`.
- Keep this slice in the existing `quantified_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded quantified-alternation backtracking-heavy surface.
- This task exists so the queue does not reach bounded quantified-alternation backtracking-heavy parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added six real benchmark workloads for the bounded quantified-alternation backtracking-heavy numbered and named `compile`/`search`/`pattern.fullmatch` slice in `benchmarks/workloads/quantified_alternation_boundary.json`, keeping only the broader-range `{1,3}` and open-ended `{1,}` follow-ons as explicit known gaps.
- Regenerated `reports/benchmarks/latest.json`; the combined benchmark publication now reports 391 workloads, 351 measured `rebar` timings, and 40 explicit known gaps, with the quantified-alternation manifest at 32 workloads, 30 measured rows, and 2 remaining gaps.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json` and `python3 -m unittest tests.benchmarks.test_quantified_alternation_boundary_benchmarks`.
