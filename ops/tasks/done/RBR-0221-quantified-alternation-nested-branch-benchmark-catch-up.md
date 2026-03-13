# RBR-0221: Catch bounded quantified-alternation nested-branch benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified-alternation nested-branch workflows supported by `RBR-0220` produce real `rebar` timings before wider counted ranges, open-ended repeats, or broader backtracking-heavy grouped execution reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/quantified_alternation_boundary.json`
- `tests/benchmarks/test_quantified_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `quantified_alternation_boundary` manifest to exercise only the bounded workflows already supported by `RBR-0220`, anchored by the existing named `pattern.fullmatch` nested-branch gap row for `a(?P<word>(b|c)|de){1,2}d` and any directly adjacent numbered or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified-alternation nested-branch workflows while leaving wider counted ranges, open-ended repeats, branch-local backreferences, conditional combinations, and broader backtracking-heavy grouped shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0220`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0220`.
- Keep this slice in the existing `quantified_alternation_boundary` manifest rather than inventing a second benchmark family for the same bounded quantified-alternation nested-branch surface.
- This task exists so the queue does not reach bounded quantified-alternation nested-branch parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added six measured quantified-alternation nested-branch benchmark rows in the existing `quantified_alternation_boundary` manifest, covering numbered and named compile/search/fullmatch companions around the old named `pattern.fullmatch` gap anchor while leaving broader counted-range, open-ended, and backtracking-heavy quantified-alternation shapes as explicit known gaps.
- Regenerated `reports/benchmarks/latest.json`; the published benchmark scorecard now reports `386` total workloads with `345` measured `rebar` timings and `41` explicit known gaps, and the `quantified-alternation-boundary` manifest now reports `27` workloads with `24` measured and `3` known gaps.
- Verified with `PYTHONPATH=python python3 -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.json --report /tmp/rebar_quantified_alt_nested_branch_bench.json`, `PYTHONPATH=python python3 -m rebar_harness.benchmarks --report reports/benchmarks/latest.json`, and `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_quantified_alternation_boundary_benchmarks`.
