# RBR-0530: Catch the nested open-ended grouped-alternation bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact nested open-ended `{1,}` grouped-alternation bytes pair already supported by `RBR-0529` produces real `rebar` timings on the existing Python-facing wider-ranged-repeat manifest before deeper bytes correctness work reopens that family.

## Deliverables
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` adds only these six bytes mirrors of the current nested open-ended grouped-alternation `str` rows:
  - `module-compile-numbered-wider-ranged-repeat-group-open-ended-cold-bytes`
  - `module-search-numbered-wider-ranged-repeat-group-open-ended-lower-bound-bc-warm-bytes`
  - `pattern-fullmatch-numbered-wider-ranged-repeat-group-open-ended-purged-bytes`
  - `module-compile-named-wider-ranged-repeat-group-open-ended-warm-bytes`
  - `module-search-named-wider-ranged-repeat-group-open-ended-lower-bound-de-warm-bytes`
  - `pattern-fullmatch-named-wider-ranged-repeat-group-open-ended-fourth-repetition-de-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|de){1,})d"` through `module.compile`, `module.search(..., b"zzabcdzz")`, and `Pattern.fullmatch(b"abcbcded")`;
  - `rb"a(?P<outer>(bc|de){1,})d"` through `module.compile`, `module.search(..., b"zzadedzz")`, and `Pattern.fullmatch(b"adededed")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the wider-ranged manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `wider-ranged-repeat-quantified-group-boundary` moves from `94` total workloads / `94` measured workloads / `0` known gaps to `100` / `100` / `0`;
  - the combined source-tree report moves from `620` total workloads / `620` measured workloads / `0` known gaps to `626` / `626` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py --report .rebar/tmp/rbr-0530-nested-open-ended-grouped-alternation-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this nested open-ended grouped-alternation pair. Do not broaden into grouped-conditionals, grouped backtracking-heavy bytes rows, or another benchmark family.

## Notes
- Build on `RBR-0529`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` currently contains only the six `-str` workload ids for this nested open-ended grouped-alternation slice and no `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `wider-ranged-repeat-quantified-group-boundary` at `94` total workloads / `94` measured workloads / `0` known gaps and the combined source-tree report at `620` total workloads / `620` measured workloads / `0` known gaps; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this run show both target bytes patterns compile plus representative `search()` / `fullmatch()` calls succeed through `rebar`, so these benchmark rows should measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0532`, which should publish the open-ended `{1,}` grouped-alternation-plus-conditional bytes pair on the existing open-ended correctness/parity path before bytes parity or benchmark catch-up widen that family.
