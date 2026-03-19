# RBR-0678: Catch the nested broader-range wider-ranged-repeat branch-local-backreference conditional callable-replacement bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement bytes pair that `RBR-0676` just moved behind `rebar._rebar` produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four bytes mirrors of the current broader `{1,4}` conditional callable-replacement `str` rows:
  - `module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-bytes`
  - `module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-bytes`
  - `pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-bytes`
  - `pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `rb"a((b|c){1,4})\\2(?(2)d|e)"` through `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbd")` and `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abbbdaccd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)"` through `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzacccccdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzacccccdabbbdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing `nested-group-callable-replacement-boundary` shared slice:
  - promote `broader-range-conditional-branch-local-backreference` from the current four `str` ids to the mixed eight-row `str` plus `bytes` slice instead of inventing another benchmark family, a bytes-only benchmark owner, or a detached expectation helper; and
  - add or update the manifest-promotion and combined-scorecard assertions so the four new bytes ids are explicitly promoted to measured rows on the existing publication surface.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `60` total workloads / `60` measured workloads / `0` known gaps to `64` / `64` / `0`;
  - the combined source-tree report moves from `751` total workloads / `751` measured workloads / `0` known gaps to `755` / `755` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader `{1,4}` conditional callable bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0678-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0676`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family, a bytes-only benchmark module, or a detached promotion helper.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding callable slice is supposed to live behind `rebar._rebar`.
- Do not broaden into replacement-template flows, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0678` is the next available feature task id in the current checkout; `RBR-0677` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0676` so the broader `{1,4}` conditional callable bytes pair reaches the same Python-path benchmark surface before a deeper grouped callable slice reopens correctness work on this family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0676-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-bytes-parity.md` records that the exact wider `{1,4}` numbered and named bytes pair now matches CPython through `rebar._rebar`, so benchmark catch-up is the adjacent bounded follow-on rather than another correctness pack;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact broader `{1,4}` conditional callable slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently keeps `broader-range-conditional-branch-local-backreference` on `nested-group-callable-replacement-boundary` as those four `str` ids only, while the same owner path already promotes the adjacent broader-range open-ended conditional callable bytes rows as measured workloads on the same manifest;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `60` total workloads / `60` measured workloads / `0` known gaps and the combined source-tree report at `751` / `751` / `0`; and
  - direct `rg` probes in this planning run confirmed the planned bytes workload ids are absent from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so this ready task is not a stale no-op.
