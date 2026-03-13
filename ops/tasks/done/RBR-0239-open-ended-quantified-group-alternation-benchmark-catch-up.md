# RBR-0239: Catch bounded open-ended quantified-group alternation benchmarks up with the new slice

Status: done
Owner: implementation
Created: 2026-03-13

## Goal
- Extend the published benchmark surface so the bounded open-ended quantified-group alternation workflows supported by `RBR-0238` produce real `rebar` timings before conditional combinations or broader grouped backtracking reopen the frontier.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/open_ended_quantified_group_boundary.json`
- `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark harness adds a dedicated `open-ended-quantified-group-boundary` manifest that exercises only the bounded workflows already supported by `RBR-0238`, anchored by a named `pattern.fullmatch` grouped-alternation row for `a(?P<word>bc|de){1,}d` and any directly adjacent numbered, compile, or module companion rows needed to publish that exact slice cleanly.
- `reports/benchmarks/latest.json` records real `rebar` timings for those supported open-ended quantified-group alternation workflows while leaving broader counted-repeat families, conditionals, and broader grouped backtracking shapes explicit as known gaps instead of silently omitting them.
- The updated benchmark rows preserve explicit cache-mode and adapter-provenance reporting and keep the main report contract intact.
- The task does not broaden regex support, alter the benchmark schema, or claim built-native full-suite publication.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0238`; do not add new execution semantics here.
- Reuse the existing benchmark adapter/provenance machinery and the current known-gap reporting style.
- Do not silently benchmark Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0238`.
- Use a dedicated benchmark manifest for this slice instead of overloading `wider_ranged_repeat_quantified_group_boundary.json`; that file only carries a non-alternation open-ended placeholder today.
- This task exists so the queue does not reach open-ended quantified-group alternation parity and then leave that newly supported slice absent from benchmark reporting.

## Completion
- Added a dedicated `open-ended-quantified-group-boundary` benchmark manifest and wired it into the default benchmark harness manifest list so the bounded `a(bc|de){1,}d` and `a(?P<word>bc|de){1,}d` slice now publishes real compile/search/fullmatch timings.
- Added focused benchmark assertions in `tests/benchmarks/test_open_ended_quantified_group_boundary_benchmarks.py` and updated the adjacent full-suite benchmark tests to account for the expanded manifest set and refreshed scorecard totals.
- Retargeted the stale open-ended placeholder in `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.json` back to an actually unsupported nested grouped-open-ended shape so the report no longer double-counts the newly supported top-level `{1,}` slice.
- Republished `reports/benchmarks/latest.json`; the combined benchmark scorecard now reports 415 workloads across 30 manifests with 377 real `rebar` timings and 38 explicit known gaps.
