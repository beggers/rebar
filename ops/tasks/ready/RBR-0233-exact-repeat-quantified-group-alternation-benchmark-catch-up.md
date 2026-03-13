# RBR-0233: Catch exact-repeat quantified-group alternation benchmarks up with the new slice

Status: ready
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded exact-repeat quantified-group alternation workflows supported by `RBR-0232` produce real `rebar` timings before wider ranged-repeat or broader counted-repeat composition reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/exact_repeat_quantified_group_boundary.json`
- `tests/benchmarks/test_exact_repeat_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `exact-repeat-quantified-group-boundary` manifest to exercise only the bounded workflows already supported by `RBR-0232`, anchored by the existing named `pattern.fullmatch` exact-repeat-group alternation gap row for `a(?P<word>bc|de){2}d` and any directly adjacent numbered, compile, or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported exact-repeat quantified-group alternation workflows while leaving broader ranged repeats and other unsupported counted-repeat combinations explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0232`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0232`.
- Keep this slice in the existing `exact-repeat-quantified-group-boundary` manifest rather than inventing a second benchmark family for the same bounded exact-repeat quantified-group alternation surface.
- This task exists so the queue does not reach exact-repeat quantified-group alternation parity and then leave that newly supported slice absent from benchmark reporting.
