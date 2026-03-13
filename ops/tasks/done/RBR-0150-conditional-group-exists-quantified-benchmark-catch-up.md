# RBR-0150: Catch bounded quantified-conditional benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded quantified-conditional workflows supported by `RBR-0149` produce real `rebar` timings before broader backtracking-heavy conditional execution reopens the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/conditional_group_exists_boundary.json`
- `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness updates the existing `conditional_group_exists_boundary` manifest to exercise only the bounded quantified-conditional workflows already supported by `RBR-0149`, anchored by the current `pattern-fullmatch-numbered-quantified-conditional-group-exists-purged-gap` row and any directly adjacent numbered or named companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported quantified-conditional workflows, such as `a(b)?c(?(1)d|e){2}` and `a(?P<word>b)?c(?(word)d|e){2}`, while leaving broader quantified conditional variants, nested conditional composition, replacement-conditioned helpers, alternation-heavy repeated arms, ranged/open-ended repeats, and broader backtracking-heavy shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0149`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0149`.
- Use the existing `pattern-fullmatch-numbered-quantified-conditional-group-exists-purged-gap` row in `benchmarks/workloads/conditional_group_exists_boundary.json` as the benchmark anchor for this slice.
- This task exists so the queue does not reach quantified-conditional parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Updated `benchmarks/workloads/conditional_group_exists_boundary.json` so the anchored numbered quantified row now publishes as a measured workload and added the named quantified `Pattern.fullmatch` companion for `a(?P<word>b)?c(?(word)d|e){2}`.
- Refreshed `tests/benchmarks/test_conditional_group_exists_boundary_benchmarks.py` to the current 29-manifest suite and asserted the new quantified conditional measured-row counts instead of the stale gap expectations.
- Republished `reports/benchmarks/latest.json`; the combined scorecard now reports `290` workloads, `236` measured workloads, and `54` known gaps, while `conditional-group-exists-boundary` reports `9` workloads with `8` measured and `1` remaining nested-conditional gap.
