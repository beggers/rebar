# RBR-0690: Catch the nested broader-range wider-ranged-repeat backtracking-heavy callable-replacement bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped backtracking-heavy callable-replacement bytes pair that `RBR-0688` just moved behind `rebar._rebar` produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four bytes mirrors of the current broader `{1,4}` backtracking-heavy callable-replacement `str` rows:
  - `module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-bytes`
  - `module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-bytes`
  - `pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-bytes`
  - `pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `rb"a(((bc|b)c){1,4})d"` through `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abcd")` and `module.subn(..., callable_match_group(group=3, prefix=b"<", suffix=b">"), b"abccdabcbccd", 1)`;
  - `rb"a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d"` through `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzabcbccbccbcdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzabccbcdabccdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing `nested-group-callable-replacement-boundary` shared slice:
  - promote `nested-broader-range-backtracking-heavy-callable-replacement` from the current four `str` ids to the mixed eight-row `str` plus `bytes` slice instead of inventing another benchmark family, a bytes-only benchmark owner, or a detached expectation helper; and
  - add or update the manifest-promotion and combined-scorecard assertions so the four new bytes ids are explicitly promoted to measured rows on the existing publication surface.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `68` total workloads / `68` measured workloads / `0` known gaps to `72` / `72` / `0`;
  - the combined source-tree report moves from `759` total workloads / `759` measured workloads / `0` known gaps to `763` / `763` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader `{1,4}` backtracking-heavy callable bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0690-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0688`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family, a bytes-only benchmark module, or a detached promotion helper.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding callable slice is supposed to live behind `rebar._rebar`.
- Do not broaden into replacement-template flows, deeper grouped execution, another grouped family, or native-path benchmark publication in this run.

## Notes
- `RBR-0690` is the next available feature task id in the current checkout; `RBR-0689` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0688` so the broader `{1,4}` nested backtracking-heavy callable bytes pair reaches the same Python-path benchmark surface before another grouped callable frontier reopens correctness work on this family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0688-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-bytes-parity.md` records that the exact wider `{1,4}` numbered and named bytes pair now matches CPython through `rebar._rebar`, so benchmark catch-up is the adjacent bounded follow-on rather than another correctness pack;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact broader `{1,4}` backtracking-heavy callable slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently keeps `nested-broader-range-backtracking-heavy-callable-replacement` on `nested-group-callable-replacement-boundary` as those four `str` ids only, while the same owner path already promotes adjacent broader-range callable bytes rows as measured workloads on the same manifest;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `68` total workloads / `68` measured workloads / `0` known gaps and the combined source-tree report at `759` / `759` / `0`; and
  - direct `rg` probes in this planning run confirmed the planned bytes workload ids are absent from `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so this ready task is not a stale no-op.

## Completion
- 2026-03-19: Added the four required broader `{1,4}` nested backtracking-heavy callable-replacement `bytes` mirrors to `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, keeping them on the existing shared manifest with the same public patterns, callback descriptors, haystacks, and module/`Pattern` entrypoints as the adjacent `str` rows.
- Updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the existing `nested-broader-range-backtracking-heavy-callable-replacement` slice, manifest-promotion assertion, and combined-scorecard assertion now promote the mixed eight-row `str` plus `bytes` surface instead of the former four-row `str` subset.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0690-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-bytes-benchmarks.py`.
- Republished `reports/benchmarks/latest.py`; the tracked publication now records `nested-group-callable-replacement-boundary` at `72` total / `72` measured / `0` known gaps and the combined source-tree benchmark report at `763` total / `763` measured / `0` known gaps.
