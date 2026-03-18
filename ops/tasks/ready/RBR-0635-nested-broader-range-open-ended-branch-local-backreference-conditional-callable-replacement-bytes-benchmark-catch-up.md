# RBR-0635: Catch the nested broader-range open-ended branch-local-backreference conditional callable-replacement bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement bytes pair produces real `rebar` timings on the existing nested-group callable benchmark manifest once `RBR-0633` lands.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four bytes mirrors of the current broader-range open-ended conditional callable-replacement `str` rows:
  - `module-sub-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-b-branch-warm-bytes`
  - `module-subn-callable-numbered-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-first-match-only-b-branch-warm-bytes`
  - `pattern-sub-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-lower-bound-c-branch-purged-bytes`
  - `pattern-subn-callable-named-open-ended-quantified-nested-group-alternation-branch-local-backreference-broader-range-conditional-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `rb"a((b|c){2,})\\2(?(2)d|e)"` through `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbbd")` and `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abbbdabcbccd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)"` through `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzacccdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzacccdabcbccdzz", 1)`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the four new rows as measured source-tree workloads on the existing `broader-range-open-ended-conditional-branch-local-backreference` slice while keeping `nested-group-callable-replacement-boundary` and the combined report at zero known gaps. Reuse the existing shared slice and zero-gap expectation surface instead of inventing another benchmark family or a bytes-only benchmark special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `44` total workloads / `44` measured workloads / `0` known gaps to `48` / `48` / `0`;
  - the combined source-tree report moves from `723` total workloads / `723` measured workloads / `0` known gaps to `727` / `727` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader-range open-ended conditional callable-replacement bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py -k "nested_broader_range_open_ended_conditional"`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0635-nested-broader-range-open-ended-branch-local-backreference-conditional-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar` by `RBR-0633`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into replacement-template flows, deeper grouped execution, another branch-local-backreference or conditional family, or native-path benchmark publication in this run.

## Notes
- Build on `RBR-0633` and the already-landed `RBR-0419` `str` benchmark slice for the same broader-range open-ended conditional callable patterns.
- Queue this directly behind `RBR-0633` so the broader `{2,}` conditional callable-replacement bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `find ops/tasks -maxdepth 2 -type f | rg 'RBR-0635'` returned no matches before this file was added;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` currently treats `broader-range-open-ended-conditional-branch-local-backreference` on `nested-group-callable-replacement-boundary` as the four `str` rows only, so the bytes follow-on can stay on the existing shared zero-gap expectation surface;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `44` total workloads / `44` measured workloads / `0` known gaps and the combined source-tree report at `723` / `723` / `0`; and
  - `reports/correctness/latest.py` still publishes `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-conditional-callable-replacement-workflows` at `16` total / `8` passed / `8` `unimplemented`, while direct `PYTHONPATH=python ./.venv/bin/python` public-API probes still raise `NotImplementedError` for the target bytes callable workflows at `rebar.sub(...)`, so `RBR-0633` remains the immediate parity head rather than a stale no-op.
