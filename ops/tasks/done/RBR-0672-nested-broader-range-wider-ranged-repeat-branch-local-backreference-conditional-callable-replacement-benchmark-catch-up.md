# RBR-0672: Catch the nested broader-range wider-ranged-repeat branch-local-backreference conditional callable-replacement pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-19
Completed: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference conditional callable-replacement `str` pair that `RBR-0670` just moved behind `rebar._rebar` produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four `str` benchmark rows for the newly landed wider `{1,4}` conditional callable slice:
  - `module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-lower-bound-b-branch-warm-str`
  - `module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-first-match-only-b-branch-warm-str`
  - `pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-all-c-purged-str`
  - `pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-conditional-upper-bound-c-branch-first-match-only-purged-str`
- The new rows stay pinned to the existing public Python-path patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `a((b|c){1,4})\\2(?(2)d|e)` through `module.sub(..., callable_match_group(group=1, suffix="x"), "abbd")` and `module.subn(..., callable_match_group(group=2, prefix="<", suffix=">"), "abbbdaccd", 1)`;
  - `a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)(?(inner)d|e)` through `Pattern.sub(..., callable_match_group(group="outer", suffix="x"), "zzacccccdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "zzacccccdabbbdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` promotes this exact wider `{1,4}` conditional callable slice as a measured zero-gap shared slice on `nested-group-callable-replacement-boundary` instead of inventing another benchmark family, a detached expectation helper, or a bytes-only special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `56` total workloads / `56` measured workloads / `0` known gaps to `60` / `60` / `0`;
  - the combined source-tree report moves from `747` total workloads / `747` measured workloads / `0` known gaps to `751` / `751` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new wider `{1,4}` conditional callable rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0672-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to Python-path benchmark catch-up for behavior already implemented by `RBR-0670`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or another manifest-local test module.
- Keep the measurements on the public `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding callable slice is supposed to live behind `rebar._rebar`.
- Do not broaden into bytes, replacement-template flows, broader callback helpers, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0672` is the next available feature task id in the current checkout; `RBR-0671` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0670` so the wider `{1,4}` conditional callable slice reaches the same Python-path benchmark surface before bytes publication or deeper grouped execution reopen the frontier.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0670-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-parity.md` records that the exact wider `{1,4}` numbered and named `str` pair now matches CPython through `rebar._rebar`, so benchmark catch-up is the adjacent bounded follow-on rather than another correctness pack;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` already owns the same callable benchmark family and currently carries the adjacent wider `{1,4}` non-conditional rows plus the broader-range open-ended `{2,}` conditional rows, but no wider `{1,4}` conditional sibling rows yet;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `56` total workloads / `56` measured workloads / `0` known gaps and the combined source-tree report at `747` / `747` / `0`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already treats the adjacent broader `{1,4}` callable slice and the broader-range open-ended conditional callable slice as measured shared expectations on the same owner path, so this follow-on can stay on that exact benchmark surface without another synthesis pass.

## Completion
- 2026-03-19: Added the four wider `{1,4}` numbered and named conditional callable `str` rows to `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, keeping the existing callback descriptors, haystacks, and public Python-path patterns on the shared owner manifest.
- 2026-03-19: Extended `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with a dedicated shared-slice expectation plus targeted manifest and scorecard promotion checks for the new zero-gap conditional callable rows, and tightened the adjacent non-conditional broader-range slice matcher to exclude `conditionals` so the shared slice inventories stay disjoint.
- 2026-03-19: Republished `reports/benchmarks/latest.py`; the tracked artifact now publishes `nested-group-callable-replacement-boundary` at `60` total workloads / `60` measured workloads / `0` known gaps and the combined source-tree report at `751` / `751` / `0`, with all four new wider `{1,4}` conditional callable rows marked `status == "measured"` through the source-tree shim path.

## Verification
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`2146 passed, 3 skipped, 1214 subtests passed`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0672-nested-broader-range-wider-ranged-repeat-branch-local-backreference-conditional-callable-replacement-benchmarks.py` (`{"known_gap_count": 0, "measured_workloads": 60, "module_workloads": 60, "parser_workloads": 0, "regression_workloads": 0, "total_workloads": 60}`)
- 2026-03-19: `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (`{"known_gap_count": 0, "measured_workloads": 751, "module_workloads": 743, "parser_workloads": 8, "regression_workloads": 5, "total_workloads": 751}`)
