# RBR-0623: Catch the nested broader-range open-ended branch-local-backreference conditional bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional bytes pair produces real `rebar` timings on the existing branch-local-backreference manifest.

## Deliverables
- `benchmarks/workloads/branch_local_backreference_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/branch_local_backreference_boundary.py` adds only these six bytes mirrors of the current broader-range open-ended nested grouped-alternation plus branch-local-backreference conditional `str` rows:
  - `module-compile-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-cold-bytes`
  - `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes`
  - `pattern-fullmatch-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-mixed-branches-purged-bytes`
  - `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-warm-bytes`
  - `module-search-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-warm-bytes`
  - `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"` through `module.compile(...)`, `module.search(..., b"zzabbbdzz")`, and `Pattern.fullmatch(b"abcbccd")`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` through `module.compile(...)`, `module.search(..., b"zzacccdzz")`, and `Pattern.fullmatch(b"abbbd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the six new rows as measured source-tree workloads while keeping `branch-local-backreference-boundary` and the combined report at zero known gaps. Reuse the existing `broader-range-open-ended-conditional-branch-local-backreference` slice and shared zero-gap expectation surface instead of inventing another benchmark family or a manifest-local bytes special case.
- Focused and combined benchmark publications move honestly:
  - `branch-local-backreference-boundary` moves from `24` total workloads / `24` measured workloads / `0` known gaps to `30` / `30` / `0`;
  - the combined source-tree report moves from `713` total workloads / `713` measured workloads / `0` known gaps to `719` / `719` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the six new broader-range open-ended conditional branch-local-backreference bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/branch_local_backreference_boundary.py --report .rebar/tmp/rbr-0623-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar`; do not add new execution semantics here.
- Reuse the existing `branch_local_backreference_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only test path.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into deeper grouped execution, replacement or callable-replacement flows, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- Build on `RBR-0621`.
- Queue this directly behind `RBR-0621` so the broader `{2,}` conditional bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `benchmarks/workloads/branch_local_backreference_boundary.py` currently contains the six adjacent `str` rows for this exact slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` currently treats `branch-local-backreference-boundary` slice `broader-range-open-ended-conditional-branch-local-backreference` as the six `str` rows only, so the bytes follow-on can stay on the existing shared zero-gap expectation surface;
  - `reports/benchmarks/latest.py` currently publishes `branch-local-backreference-boundary` at `24` total workloads / `24` measured workloads / `0` known gaps and the combined source-tree report at `713` / `713` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0621` until parity lands.

## Completion
- 2026-03-18: Added the six bytes mirrors for the broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional slice to `benchmarks/workloads/branch_local_backreference_boundary.py`, promoted them on the shared zero-gap benchmark expectation surface in `tests/benchmarks/benchmark_expectations.py`, and regenerated `reports/benchmarks/latest.py`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`33 passed`, `1074` subtests), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/branch_local_backreference_boundary.py --report .rebar/tmp/rbr-0623-nested-broader-range-open-ended-branch-local-backreference-conditional-bytes-benchmarks.py` (`30` total / `30` measured / `0` known gaps), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`, which now publishes `branch-local-backreference-boundary` at `30 / 30 / 0` and the combined source-tree report at `719 / 719 / 0` through the `source-tree-shim` path.
