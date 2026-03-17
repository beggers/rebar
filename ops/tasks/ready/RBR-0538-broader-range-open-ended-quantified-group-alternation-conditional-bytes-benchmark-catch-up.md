# RBR-0538: Catch the broader-range open-ended grouped-alternation-plus-conditional bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` grouped-alternation-plus-conditional bytes pair already supported by `RBR-0537` produces real `rebar` timings on the existing Python-facing open-ended manifest before broader-range open-ended grouped backtracking-heavy bytes publication reopens that family.

## Deliverables
- `benchmarks/workloads/open_ended_quantified_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/open_ended_quantified_group_boundary.py` adds only these six bytes mirrors of the current broader-range grouped-conditional `str` rows:
  - `module-compile-numbered-open-ended-group-broader-range-conditional-cold-bytes`
  - `module-search-numbered-open-ended-group-broader-range-conditional-second-repetition-bc-warm-bytes`
  - `pattern-fullmatch-numbered-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes`
  - `module-compile-named-open-ended-group-broader-range-conditional-warm-bytes`
  - `module-search-named-open-ended-group-broader-range-conditional-fourth-repetition-de-warm-bytes`
  - `pattern-fullmatch-named-open-ended-group-broader-range-conditional-third-repetition-mixed-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((bc|de){2,})?(?(1)d|e)"` through `module.compile`, `module.search(..., b"zzabcbcdzz")`, and `Pattern.fullmatch(b"abcbcded")`;
  - `rb"a(?P<outer>(bc|de){2,})?(?(outer)d|e)"` through `module.compile`, `module.search(..., b"zzadedededzz")`, and `Pattern.fullmatch(b"abcbcded")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping the open-ended manifest and combined report at zero known gaps.
- Focused and combined benchmark publications move honestly:
  - `open-ended-quantified-group-boundary` moves from `42` total workloads / `42` measured workloads / `0` known gaps to `48` / `48` / `0`;
  - the combined source-tree report moves from `632` total workloads / `632` measured workloads / `0` known gaps to `638` / `638` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/open_ended_quantified_group_boundary.py --report .rebar/tmp/rbr-0538-broader-range-open-ended-grouped-conditional-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark catch-up only. Do not change correctness fixtures, parity suites, or `reports/correctness/latest.py`.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not broaden into built-native publication, benchmark-harness refactors, or new adapter modes in this run.
- Add only the directly adjacent bytes mirrors for this broader-range grouped-conditional pair. Do not broaden into broader-range open-ended grouped backtracking-heavy bytes correctness publication, runtime parity follow-ons, or another benchmark family.

## Notes
- Build on `RBR-0537`.
- 2026-03-17 feature-planning probes confirm this task is not stale:
  - `benchmarks/workloads/open_ended_quantified_group_boundary.py` currently contains only the six existing broader-range grouped-conditional source-tree rows for this slice and none of the six planned `-bytes` mirrors;
  - `reports/benchmarks/latest.py` currently publishes `open-ended-quantified-group-boundary` at `42` total workloads / `42` measured workloads / `0` known gaps and the combined source-tree report at `632` total / `632` measured / `0` known gaps; and
  - `ops/tasks/done/RBR-0537-broader-range-open-ended-quantified-group-alternation-conditional-bytes-parity.md` already records successful public-API parity for `rb"a((bc|de){2,})?(?(1)d|e)"` and `rb"a(?P<outer>(bc|de){2,})?(?(outer)d|e)"`, so these benchmark rows should measure rather than reopen a runtime gap.
- The surviving follow-on after this task is `RBR-0539`, which should publish the broader-range open-ended `{2,}` grouped backtracking-heavy bytes pair on the existing correctness/parity path before bytes parity or benchmark catch-up revisit the open-ended family.
