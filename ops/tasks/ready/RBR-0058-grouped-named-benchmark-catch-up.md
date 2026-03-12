# RBR-0058: Catch grouped and named workflow benchmarks up with the new behavior slices

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Extend the published benchmark surface so newly supported grouped-capture, named-group, named-template, and named-backreference workflows produce real `rebar` timings instead of leaving the benchmark report another milestone behind the correctness frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/grouped_named_boundary.json`
- `tests/benchmarks/test_grouped_named_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness publishes a dedicated grouped/named workflow manifest that exercises only the bounded grouped and named behavior slices already supported by `RBR-0051`, `RBR-0053`, `RBR-0055`, and `RBR-0057`.
- `reports/benchmarks/latest.json` records real `rebar` timings for the supported grouped/named workflows while leaving any still-unsupported grouped or reference cases explicit as known gaps instead of silently omitting them.
- The new benchmark rows cover both module and compiled-`Pattern` entrypoints where the corresponding correctness tasks already established parity, and they preserve explicit cache-mode and adapter-provenance reporting.
- The task does not claim built-native full-suite publication; it keeps the existing full report contract intact and remains honest about source-tree-shim versus built-native execution mode.

## Constraints
- Keep this task scoped to benchmark catch-up for grouped and named behavior that already exists by the time the task runs; do not broaden regex support, rework the benchmark schema, or fabricate timings for unsupported cases.
- Reuse the existing benchmark adapter/provenance machinery and follow the same explicit known-gap reporting used by the current published manifests.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0048`, `RBR-0051`, `RBR-0053`, `RBR-0055`, and `RBR-0057`.
- This task exists so grouped and named behavior work reaches the published benchmark report promptly instead of piling up as correctness-only wins.
