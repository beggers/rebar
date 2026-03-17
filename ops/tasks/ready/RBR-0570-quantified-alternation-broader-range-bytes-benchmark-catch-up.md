# RBR-0570: Catch the quantified-alternation broader-range bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range `{1,3}` quantified-alternation bytes pair expected to be supported by `RBR-0568` produces real `rebar` timings on the existing Python-facing quantified-alternation manifest.

## Deliverables
- `benchmarks/workloads/quantified_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/quantified_alternation_boundary.py` adds only these six bytes mirrors of the current broader-range quantified-alternation `str` rows:
  - `module-compile-numbered-quantified-alternation-broader-range-cold-bytes`
  - `module-search-numbered-quantified-alternation-broader-range-third-repetition-cold-bytes`
  - `pattern-fullmatch-numbered-quantified-alternation-broader-range-third-repetition-bcb-purged-bytes`
  - `module-compile-named-quantified-alternation-broader-range-warm-bytes`
  - `module-search-named-quantified-alternation-broader-range-third-repetition-bcc-warm-bytes`
  - `pattern-fullmatch-named-quantified-alternation-broader-range-third-repetition-bbb-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a(b|c){1,3}d"` through `module.compile`, `module.search(..., b"zzabccdzz")`, and `Pattern.fullmatch(b"abcbd")`;
  - `rb"a(?P<word>b|c){1,3}d"` through `module.compile`, `module.search(..., b"zzabccdzz")`, and `Pattern.fullmatch(b"abbbd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the quantified-alternation manifest and the combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `quantified-alternation-boundary` moves from `48` total workloads / `48` measured workloads / `0` known gaps to `54` / `54` / `0`;
  - the combined source-tree report moves from `668` total workloads / `668` measured workloads / `0` known gaps to `674` / `674` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/quantified_alternation_boundary.py --report .rebar/tmp/rbr-0570-quantified-alternation-broader-range-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this broader-range quantified-alternation pair. Do not broaden into open-ended quantified-alternation bytes work, nested-branch bytes work, conditional bytes work, backtracking-heavy bytes work, or another benchmark family in this run.

## Notes
- Build on `RBR-0568`.
- 2026-03-17 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `benchmarks/workloads/quantified_alternation_boundary.py` currently contains the six broader-range quantified-alternation `str` workloads for this exact `{1,3}` slice and none of the planned `-bytes` mirrors;
  - the benchmark expectation and shared source-tree benchmark suites currently contain no exact-id coverage for those six broader-range bytes rows, so the follow-on can stay on the existing quantified-alternation manifest/test surface instead of inventing another benchmark family;
  - `reports/benchmarks/latest.py` currently publishes `quantified-alternation-boundary` at `48` total workloads / `48` measured workloads / `0` known gaps and the combined source-tree report at `668` / `668` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0568` until parity lands.
