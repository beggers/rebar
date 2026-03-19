# RBR-0665: Catch the nested broader-range wider-ranged-repeat branch-local-backreference callable-replacement bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped-alternation plus branch-local-backreference callable-replacement bytes pair produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest once `RBR-0663` lands.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four bytes mirrors of the current broader `{1,4}` callable-replacement `str` rows:
  - `module-sub-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes`
  - `module-subn-callable-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-first-match-only-warm-bytes`
  - `pattern-sub-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-bytes`
  - `pattern-subn-callable-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `rb"a((b|c){1,4})\\2d"` through `module.sub(..., callable_match_group(group=1, suffix=b"x"), b"abbd")` and `module.subn(..., callable_match_group(group=2, prefix=b"<", suffix=b">"), b"abcbccdabbd", 1)`;
  - `rb"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` through `Pattern.sub(..., callable_match_group(group="outer", suffix=b"x"), b"zzacccccdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix=b"<", suffix=b">"), b"zzacccccdabbbdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treats `broader-range-branch-local-backreference` on `nested-group-callable-replacement-boundary` as the measured zero-gap shared slice with the four new bytes rows plus the existing four `str` rows:
  - keep this bytes follow-on on the existing shared slice and zero-gap manifest path rather than inventing another benchmark family, a bytes-only benchmark owner, or a second detached expectation helper;
  - add or update the manifest-promotion assertion so those four new bytes ids are explicitly promoted to measured rows on the existing `nested-group-callable-replacement-boundary` publication surface.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `52` total workloads / `52` measured workloads / `0` known gaps to `56` / `56` / `0`;
  - the combined source-tree report moves from `743` total workloads / `743` measured workloads / `0` known gaps to `747` / `747` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader `{1,4}` callable-replacement bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0665-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar` by `RBR-0663`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into the adjacent replacement-template flows, conditional callable flows, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0665` is the next available feature task id in the current checkout; `RBR-0664` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0663` so the broader `{1,4}` callable-replacement bytes pair reaches the same Python-path benchmark surface before deeper grouped execution broadens that family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `reports/correctness/latest.py` currently publishes `1334` total / `1326` passed / `8` `unimplemented` overall, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference.callable` still reads `16` total / `8` passed / `8` `unimplemented`, so ready `RBR-0663` remains the immediate parity head rather than a stale no-op;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the four adjacent `str` rows for this exact broader `{1,4}` callable slice and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently treats `broader-range-branch-local-backreference` on `nested-group-callable-replacement-boundary` as the four `str` rows only, while the same owner already promotes the adjacent broader-range open-ended callable bytes rows on that manifest as measured workloads;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `52` total workloads / `52` measured workloads / `0` known gaps and the combined source-tree report at `743` / `743` / `0`; and
  - the four adjacent `str` benchmark rows already pin the exact public-path patterns, callable descriptors, and haystacks this bytes follow-on should mirror without another synthesis pass.

## Completion Notes
- 2026-03-19: Added the four broader `{1,4}` bytes callable-replacement rows to `benchmarks/workloads/nested_group_callable_replacement_boundary.py`, keeping the existing `text_model == "bytes"` manifest encoding and the shared `nested-group-callable-replacement-boundary` surface.
- Expanded `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the `broader-range-branch-local-backreference` slice now expects the four new bytes ids alongside the existing four `str` ids, and added explicit manifest/scorecard promotion assertions for those bytes rows.
- Regenerated `reports/benchmarks/latest.py`; the tracked report now publishes `nested-group-callable-replacement-boundary` at `56` total workloads / `56` measured workloads / `0` known gaps and the combined source-tree suite at `747` total workloads / `747` measured workloads / `0` known gaps, with all four new bytes rows marked `status == "measured"` and `implementation_timing.status == "measured"` through the source-tree shim path.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0665-nested-broader-range-wider-ranged-repeat-branch-local-backreference-callable-replacement-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`
