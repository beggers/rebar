# RBR-0218: Catch bounded quantified-alternation-plus-conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified-alternation-plus-conditional workflows supported by `RBR-0217` produce real `rebar` timings before broader counted-repeat backtracking-heavy execution reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `quantified_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0217`, anchored by the existing numbered `module.search` conditional gap row for `a((b|c){1,2})?(?(1)d|e)` and any directly adjacent named or compiled-`Pattern` companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified-alternation-plus-conditional workflows while leaving broader counted ranges, branch-local backreferences, backtracking-heavy alternation shapes, and broader conditional compositions explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0217`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0217`.
- Keep this slice in the existing `quantified_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded quantified-alternation-plus-conditional surface.
- This task exists so the queue does not reach bounded quantified-alternation-plus-conditional parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added numbered and named quantified-alternation-plus-conditional compile/search/fullmatch benchmark rows to the existing `quantified_alternation_boundary` manifest, reusing the old numbered `module.search` conditional gap anchor and leaving broader counted ranges, nested branches, open-ended repeats, and backtracking-heavy shapes as explicit known gaps.
- Regenerated `reports/benchmarks/latest.json`, moving the published benchmark surface to 381 workloads with 339 measured `rebar` timings and 42 explicit known gaps; the `quantified-alternation-boundary` manifest now reports 22 workloads with 18 measured and 4 known gaps.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.json --report /tmp/rebar_quantified_alt_conditional_bench.json` and `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_quantified_alternation_boundary_benchmarks`.
