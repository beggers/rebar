# RBR-0684: Catch the nested broader-range wider-ranged-repeat backtracking-heavy callable-replacement pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader `{1,4}` nested grouped backtracking-heavy callable-replacement `str` pair that `RBR-0682` just moved behind `rebar._rebar` produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four `str` benchmark rows for the newly landed broader `{1,4}` nested grouped backtracking-heavy callable slice:
  - `module-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str`
  - `module-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str`
  - `pattern-sub-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-upper-bound-mixed-purged-str`
  - `pattern-subn-callable-nested-broader-range-wider-ranged-repeat-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str`
- The new rows stay pinned to the existing public Python-path patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `a(((bc|b)c){1,4})d` through `module.sub(..., callable_match_group(group=1, suffix="x"), "abcd")` and `module.subn(..., callable_match_group(group=3, prefix="<", suffix=">"), "abccdabcbccd", 1)`;
  - `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d` through `Pattern.sub(..., callable_match_group(group="outer", suffix="x"), "zzabcbccbccbcdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "zzabccbcdabccdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing `nested-group-callable-replacement-boundary` shared slice:
  - promote the new broader `{1,4}` nested grouped backtracking-heavy callable slice as measured zero-gap shared coverage instead of inventing another benchmark family, detached expectation helper, or manifest-local assertion path; and
  - add or update the manifest-promotion and combined-scorecard assertions so the four new workload ids are explicitly promoted to measured rows on the tracked publication surface.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `64` total workloads / `64` measured workloads / `0` known gaps to `68` / `68` / `0`;
  - the combined source-tree report moves from `755` total workloads / `755` measured workloads / `0` known gaps to `759` / `759` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader `{1,4}` nested grouped backtracking-heavy callable rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0684-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to Python-path benchmark catch-up for behavior already implemented by `RBR-0682`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or another manifest-local test module.
- Keep the measurements on the public `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding callable slice is supposed to live behind `rebar._rebar`.
- Do not broaden into bytes, replacement-template flows, broader callback helpers, branch-local-backreference follow-ons, deeper grouped execution, or native-path benchmark publication in this run.

## Notes
- `RBR-0684` is the next available feature task id in the current checkout; `RBR-0683` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind `RBR-0682` so the broader `{1,4}` nested backtracking-heavy callable slice reaches the same Python-path benchmark surface before bytes, grouped replacement, or deeper grouped execution reopen the frontier.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0682-nested-broader-range-wider-ranged-repeat-backtracking-heavy-callable-replacement-parity.md` records that the exact broader `{1,4}` numbered and named `str` pair now matches CPython through `rebar._rebar`, so benchmark catch-up is the adjacent bounded follow-on rather than another correctness pack;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains `64` workloads, zero `backtracking-heavy` rows, and no workloads for `a(((bc|b)c){1,4})d` or `a(?P<outer>(?:(?P<inner>bc|b)c){1,4})d`;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `64` total workloads / `64` measured workloads / `0` known gaps and the combined source-tree report at `755` / `755` / `0`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already treats the adjacent callable owner slices as shared zero-gap benchmark expectations, so this follow-on can stay on that exact benchmark surface without another synthesis pass.
