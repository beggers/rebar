# RBR-0523: Catch the nested broader-range wider-ranged-repeat grouped-alternation bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact nested broader `{1,4}` grouped-alternation bytes pair already supported by `RBR-0522` produces real `rebar` timings on the existing Python-facing wider-ranged-repeat manifest before nested broader grouped-conditionals reopen correctness work.

## Deliverables
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` adds only these six bytes mirrors of the current nested broader grouped-alternation `str` rows:
  - `module-compile-numbered-wider-ranged-repeat-group-nested-broader-range-cold-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-nested-broader-range-lower-bound-bc-warm-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-nested-broader-range-third-repetition-mixed-purged-bytes`
  - `module-compile-named-wider-ranged-repeat-group-nested-broader-range-warm-bytes`
  - `module-search-named-wider-ranged-repeat-group-nested-broader-range-lower-bound-de-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-group-nested-broader-range-upper-bound-all-de-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|de){1,4})d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, and `Pattern.fullmatch(b"abcbcded")`;
  - `rb"a(?P<outer>(bc|de){1,4})d"` through `module.compile`, `module.search(..., b"zzadedzz")`, and `Pattern.fullmatch(b"adedededed")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the wider-ranged manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `wider-ranged-repeat-quantified-group-boundary` moves from `81` total workloads / `81` measured workloads / `0` known gaps to `87` / `87` / `0`;
  - the combined source-tree report moves from `607` total workloads / `607` measured workloads / `0` known gaps to `613` / `613` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0523-nested-broader-range-grouped-alternation-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this nested broader grouped-alternation pair. Do not broaden into nested broader grouped-conditional bytes rows, open-ended repeats, or another benchmark family.

## Notes
- Build on `RBR-0522`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` currently contains only the six `-str` workload ids for this nested broader grouped-alternation slice and no `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `wider-ranged-repeat-quantified-group-boundary` at `81` total workloads / `81` measured workloads / `0` known gaps and the combined source-tree report at `607` total workloads / `607` measured workloads / `0` known gaps; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes now show both target bytes patterns compile and search successfully through `rebar`, so these benchmark rows should measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0524`, which should publish the nested broader `{1,4}` bytes grouped-conditional pair on the existing correctness/parity path before bytes parity or benchmark catch-up revisit that family.
