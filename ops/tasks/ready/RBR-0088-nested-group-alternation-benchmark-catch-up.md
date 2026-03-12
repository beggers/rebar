# RBR-0088: Catch nested-group alternation benchmarks up with the new bounded slice

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so the bounded nested-group alternation workflows supported by `RBR-0087` produce real `rebar` timings before the queue reopens a broader correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/nested_group_alternation_boundary.json`
- `tests/benchmarks/test_nested_group_alternation_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated nested-group alternation manifest that exercises only the bounded workflows already supported by `RBR-0087`, such as `a((b|c))d` and `a(?P<outer>(?P<inner>b|c))d` through module and compiled-`Pattern` entrypoints.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported nested-group alternation workflows while leaving broader nested-group, multi-alternation, quantified-branch, or branch-local backreference shapes explicit as known gaps instead of silently omitting them.
- The new benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0087`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0087`.
- This task exists so the queue does not reach bounded nested-group alternation parity and then leave that newly supported slice absent from benchmark reporting.
