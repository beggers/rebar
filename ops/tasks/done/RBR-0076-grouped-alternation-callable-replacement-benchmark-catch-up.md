# RBR-0076: Catch grouped-alternation callable-replacement benchmarks up with the new combined slice

Status: done
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded grouped-alternation callable-replacement workflows supported by `RBR-0075` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_alternation_callable_replacement_boundary.json`
- `tests/benchmarks/test_grouped_alternation_callable_replacement_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated grouped-alternation callable-replacement manifest that exercises only the bounded `sub()` and `subn()` callable workflows already supported by `RBR-0075`, such as `a(b|c)d` with a callable using `match.group(1)` and `a(?P<word>b|c)d` with a callable using `match.group("word")` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported grouped-alternation callable-replacement workflows while leaving broader grouped, alternation, or callback shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0075`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0073` and `RBR-0075`.
- This task exists so the queue does not reach grouped-alternation callable-replacement parity and then leave that newly supported combined slice absent from benchmark reporting.

## Completion Notes
- Added a dedicated `grouped-alternation-callable-replacement-boundary` benchmark manifest covering the bounded module and compiled-`Pattern` `sub()`/`subn()` callback workflows already supported by `RBR-0075`, plus two explicit nested-group gap rows.
- Extended `python/rebar_harness/benchmarks.py` so benchmark manifests can describe callable replacements with the same small JSON callback descriptors already used by the correctness fixtures, while preserving the existing string-replacement path.
- Regenerated `reports/benchmarks/latest.json`; the published combined benchmark scorecard now covers 104 workloads with 81 measured `rebar` timings and 23 explicit known gaps.
- Verified with `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_grouped_alternation_callable_replacement_boundary_benchmarks` and `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_grouped_alternation_replacement_boundary_benchmarks`.
