# RBR-0251: Catch open-ended quantified-group alternation backtracking-heavy benchmarks up with the new slice

Status: in_progress
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded open-ended grouped backtracking-heavy `{1,}` workflows supported by `RBR-0250` produce real `rebar` timings before larger counted ranges or broader grouped-conditionals reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/open_ended_quantified_group_boundary.json`
- `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness promotes the existing `pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap` anchor into measured coverage and adds only the directly adjacent numbered or named compile/module/pattern companion rows needed to publish this exact bounded slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported open-ended grouped backtracking-heavy workflows while leaving broader counted ranges, replacement semantics, and broader grouped-conditionals explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, split out a new benchmark family, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0250`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0250`.
- Reuse the existing `pattern-fullmatch-named-open-ended-group-backtracking-heavy-purged-gap` row as the benchmark anchor instead of forking another manifest.
- This task exists so the queue does not reach open-ended grouped backtracking-heavy parity and then leave that newly supported slice absent from benchmark reporting.
