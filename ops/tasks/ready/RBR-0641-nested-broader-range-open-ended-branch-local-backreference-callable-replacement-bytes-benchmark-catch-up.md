# RBR-0641: Catch the nested broader-range open-ended branch-local-backreference callable-replacement bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference callable-replacement bytes pair produces real `rebar` timings on the existing nested-group callable benchmark manifest once `RBR-0639` lands.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four bytes mirrors of the current broader-range open-ended callable-replacement `str` rows:
  - `module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes`
  - `module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-first-match-only-b-branch-warm-bytes`
  - `pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes`
  - `pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `rb"a((b|c){2,})\\2d"` through `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbbd")` and `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abbbdabcbccd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"` through `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzacccdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzacccdabcbccdzz", 1)`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat `broader-range-open-ended-branch-local-backreference` on `nested-group-callable-replacement-boundary` as the measured zero-gap shared slice with the four new bytes rows plus the existing four `str` rows. Reuse the existing shared slice and zero-gap expectation surface instead of inventing another benchmark family or a bytes-only benchmark special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `48` total workloads / `48` measured workloads / `0` known gaps to `52` / `52` / `0`;
  - the combined source-tree report moves from `727` total workloads / `727` measured workloads / `0` known gaps to `731` / `731` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader-range open-ended callable-replacement bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0641-nested-broader-range-open-ended-branch-local-backreference-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar` by `RBR-0639`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into the adjacent conditional callable flows, replacement-template flows, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0641` is the next available feature task id in the current checkout; `RBR-0640` is already occupied by the done architecture cleanup task.
- Queue this directly behind `RBR-0639` so the broader `{2,}` callable-replacement bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0641'` returned no matches before this file was added;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact non-conditional slice and none of the planned `-bytes` mirrors, while the same manifest already carries the four conditional bytes rows landed by `RBR-0635`;
  - `tests/benchmarks/benchmark_expectations.py` currently treats `broader-range-open-ended-branch-local-backreference` on `nested-group-callable-replacement-boundary` as the four `str` rows only, and the benchmark scorecard tests currently promote bytes rows only for the adjacent conditional slice;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `48` total workloads / `48` measured workloads / `0` known gaps and the combined source-tree report at `727` / `727` / `0`; and
  - a direct `PYTHONPATH=python ./.venv/bin/python` public-API probe from this planning run still raises `NotImplementedError` for `rebar.sub(rb"a((b|c){2,})\\2d", ...)`, so `RBR-0639` remains the immediate parity head rather than a stale no-op.
