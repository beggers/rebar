# RBR-0653: Catch the nested broader-range wider-ranged-repeat branch-local-backreference replacement-template slice up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` counted-repeat nested grouped-alternation plus branch-local-backreference replacement-template `str` slice produces real `rebar` timings on the existing nested-group replacement manifest once the same slice is live behind `rebar._rebar`.

## Deliverables
- `benchmarks/workloads/nested_group_replacement_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_replacement_boundary.py` adds only these four `str` workloads for the broader `{1,4}` nested replacement-template slice:
  - `module-sub-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-str`
  - `module-subn-template-numbered-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-str`
  - `pattern-sub-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-all-c-purged-str`
  - `pattern-subn-template-named-wider-ranged-repeat-quantified-nested-group-alternation-branch-local-backreference-upper-bound-c-branch-first-match-only-purged-str`
- The new rows stay pinned to the existing Python-facing public patterns, replacements, and haystacks for this exact bounded slice:
  - `r"a((b|c){1,4})\\2d"` through `module.sub(..., r"\\1x", "abbd")` and `module.subn(..., r"\\2x", "abbbdaccd", 1)`;
  - `r"a(?P<outer>(?P<inner>b|c){1,4})(?P=inner)d"` through `Pattern.sub(r"\\g<outer>x", "zzacccccdzz")` and `Pattern.subn(r"\\g<inner>x", "zzacccccdabbbdzz", 1)`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the four new rows as measured source-tree workloads on the existing `nested-group-replacement-boundary` manifest by adding the missing `broader-range-branch-local-backreference` replacement-template slice, while keeping that manifest and the combined benchmark report at zero known gaps. Reuse the shared zero-gap expectation surface instead of inventing another benchmark family or a manifest-local special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-replacement-boundary` moves from `32` total workloads / `32` measured workloads / `0` known gaps to `36` / `36` / `0`;
  - the combined source-tree report moves from `735` total workloads / `735` measured workloads / `0` known gaps to `739` / `739` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader `{1,4}` replacement-template rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_replacement_boundary.py --report .rebar/tmp/rbr-0653-nested-broader-range-wider-ranged-repeat-branch-local-backreference-replacement-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for the behavior targeted behind `rebar._rebar` by `RBR-0651`; do not add new replacement semantics here.
- Reuse the existing `nested_group_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or another replacement-specific benchmark module.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.
- Do not broaden into bytes, conditional replacements, callable replacements, deeper grouped execution, another branch-local-backreference family, or native-path benchmark publication in this run.

## Notes
- `RBR-0653` is the next available feature task id in the current checkout; `RBR-0652` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Build on `RBR-0651`.
- Queue this directly behind `RBR-0651` so the same broader `{1,4}` replacement-template slice reaches the shared Python-path benchmark surface before bytes mirrors, conditional replacement follow-ons, or deeper grouped execution broaden that family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `reports/correctness/latest.py` still publishes `1318` total / `1310` passed / `8` `unimplemented`, and `collection.replacement.nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference` still reports `8` total / `0` passed / `8` `unimplemented`, so `RBR-0651` remains the immediate parity head rather than a stale no-op;
  - `benchmarks/workloads/nested_group_replacement_boundary.py` currently contains the open-ended `{1,}` and broader-range open-ended `{2,}` non-conditional replacement-template rows plus the broader-range open-ended `{2,}` conditional rows, but no wider-ranged-repeat `{1,4}` sibling for this same replacement-template family;
  - `tests/benchmarks/benchmark_expectations.py` already publishes the adjacent broader `{1,4}` callable-replacement slice on the same owner path and currently carries no corresponding `nested-group-replacement-boundary` expectation for the non-callable template slice, so the new benchmark work can stay on the shared expectation surface without another synthesis pass;
  - `tests/conformance/fixtures/nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_replacement_workflows.py` and the ready `RBR-0651` task already pin the exact patterns, replacement templates, haystacks, and representative lower-bound / first-match-only / upper-bound owner shapes this benchmark follow-on should mirror; and
  - `reports/benchmarks/latest.py` currently publishes `nested-group-replacement-boundary` at `32` total workloads / `32` measured workloads / `0` known gaps and the combined source-tree report at `735` / `735` / `0`, so the expected `36`-workload manifest and `739`-workload combined target are concrete before implementation starts.
