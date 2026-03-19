# RBR-0702: Catch the nested broader-range open-ended backtracking-heavy callable-replacement bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped backtracking-heavy callable-replacement bytes pair that `RBR-0700` just moved behind `rebar._rebar` produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four bytes mirrors of the current broader-range open-ended `{2,}` backtracking-heavy callable-replacement `str` rows:
  - `module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes`
  - `module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes`
  - `pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-bytes`
  - `pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `rb"a(((bc|b)c){2,})d"` through `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abcbcd")` and `module.subn(..., callable_match_group(group=3, prefix=b"<", suffix=b">"), b"abccbccdabcbcd", 1)`;
  - `rb"a(?P<outer>(?:(?P<inner>bc|b)c){2,})d"` through `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzabcbcbcbcdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzabcbcbcbcdabccbccdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing `nested-group-callable-replacement-boundary` shared slice:
  - promote the broader-range open-ended backtracking-heavy callable-replacement slice from the current four `str` ids to the mixed eight-row `str` plus `bytes` slice instead of inventing another benchmark family, a bytes-only benchmark owner, or a detached expectation helper; and
  - add or update the manifest-promotion and combined-scorecard assertions so the four new bytes ids are explicitly promoted to measured rows on the existing publication surface.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `76` total workloads / `76` measured workloads / `0` known gaps to `80` / `80` / `0`;
  - the combined source-tree report moves from `767` total workloads / `767` measured workloads / `0` known gaps to `771` / `771` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader-range open-ended `{2,}` backtracking-heavy callable bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0702-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0700`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family, a bytes-only benchmark module, or a detached promotion helper.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding callable slice is supposed to live behind `rebar._rebar`.
- Do not broaden into replacement-template flows, deeper grouped execution, another grouped family, or native-path benchmark publication in this run.

## Notes
- `RBR-0702` is the next available feature task id in the current checkout; `RBR-0701` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind the drained `RBR-0700` head so the broader-range open-ended `{2,}` nested backtracking-heavy callable bytes pair reaches the same Python-path benchmark surface before another grouped callable frontier reopens correctness work on this family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0700-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-bytes-parity.md` records that the exact open-ended `{2,}` numbered and named bytes pair now matches CPython through `rebar._rebar`, so benchmark catch-up is the adjacent bounded follow-on rather than another correctness pack;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact broader-range open-ended `{2,}` backtracking-heavy callable slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently keeps the broader-range open-ended backtracking-heavy callable slice on `nested-group-callable-replacement-boundary` as those four `str` ids only, while the same owner path already promotes adjacent callable bytes rows as measured workloads on the same manifest;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `76` total workloads / `76` measured workloads / `0` known gaps and the combined source-tree report at `767` / `767` / `0`; and
  - direct `rg` probes in this planning run confirmed the planned bytes workload ids are absent from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so this ready task is not a stale no-op.
