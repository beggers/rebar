# RBR-0527: Catch the nested broader-range wider-ranged-repeat grouped-conditional bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact nested broader `{1,4}` grouped-conditional bytes pair already supported by `RBR-0525` produces real `rebar` timings on the existing Python-facing wider-ranged-repeat manifest before the next adjacent bytes correctness slice reopens that family.

## Deliverables
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` adds only these seven bytes mirrors of the current nested broader grouped-conditional `str` rows:
  - `module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-cold-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-absent-warm-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-bc-warm-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-conditional-mixed-purged-bytes`
  - `module-compile-named-wider-ranged-repeat-group-nested-broader-range-conditional-warm-bytes`
  - `module-search-named-wider-ranged-repeat-group-nested-broader-range-conditional-lower-bound-de-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-conditional-upper-bound-all-de-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(((bc|de){1,4})d)?(?(1)e|f)"` through `module.compile`, `module.search(..., b"zzafzz")`, `module.search(..., b"zzabcdezz")`, and `Pattern.fullmatch(b"abcbcdede")`;
  - `rb"a(?P<outer>((bc|de){1,4})d)?(?(outer)e|f)"` through `module.compile`, `module.search(..., b"zzadedezz")`, and `Pattern.fullmatch(b"adedededede")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the seven new rows as measured source-tree workloads while keeping the wider-ranged manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `wider-ranged-repeat-quantified-group-boundary` moves from `87` total workloads / `87` measured workloads / `0` known gaps to `94` / `94` / `0`;
  - the combined source-tree report moves from `613` total workloads / `613` measured workloads / `0` known gaps to `620` / `620` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the seven new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0527-nested-broader-range-grouped-conditional-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this nested broader grouped-conditional pair. Do not broaden into nested open-ended grouped bytes publication, nested broader grouped backtracking-heavy bytes work, or another benchmark family.

## Notes
- Build on `RBR-0525`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` currently contains only the seven `-str` workload ids for this nested broader grouped-conditional slice and no `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `wider-ranged-repeat-quantified-group-boundary` at `87` total workloads / `87` measured workloads / `0` known gaps and the combined source-tree report at `613` total workloads / `613` measured workloads / `0` known gaps; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes now show both target bytes patterns compile plus representative `search()` / `fullmatch()` calls succeed through `rebar`, so these benchmark rows should measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0528`, which should publish the nested open-ended `{1,}` grouped-alternation bytes pair on the existing open-ended correctness/parity path before bytes parity or benchmark catch-up widen that family.
