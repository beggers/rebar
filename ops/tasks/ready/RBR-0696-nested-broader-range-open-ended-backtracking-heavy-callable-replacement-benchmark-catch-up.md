# RBR-0696: Catch the nested broader-range open-ended backtracking-heavy callable-replacement pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped backtracking-heavy callable-replacement `str` pair that `RBR-0694` just moved behind `rebar._rebar` produces real `rebar` timings on the existing `nested-group-callable-replacement-boundary` manifest.

## Deliverables
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_callable_replacement_boundary.py` adds only these four `str` rows for the current broader-range open-ended backtracking-heavy callable-replacement slice:
  - `module-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-lower-bound-short-branch-warm-str`
  - `module-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-numbered-first-match-only-long-branch-warm-str`
  - `pattern-sub-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-fourth-repetition-short-only-purged-str`
  - `pattern-subn-callable-nested-broader-range-open-ended-quantified-group-alternation-backtracking-heavy-named-b-branch-first-match-only-purged-str`
- The new rows stay pinned to the existing Python-path public patterns, callback descriptors, and haystacks for this exact bounded slice:
  - `a(((bc|b)c){2,})d` through `module.sub(..., callable_match_group(group=1, suffix="x"), "abcbcd")` and `module.subn(..., callable_match_group(group=3, prefix="<", suffix=">"), "abccbccdabcbcd", 1)`;
  - `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d` through `Pattern.sub(..., callable_match_group(group="outer", suffix="x"), "zzabcbcbcbcdzz")` and `Pattern.subn(..., callable_match_group(group="inner", prefix="<", suffix=">"), "zzabcbcbcbcdabccbccdzz", 1)`.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing `nested-group-callable-replacement-boundary` shared benchmark owner:
  - add or update the manifest-promotion and combined-slice assertions so these four workload ids are explicitly promoted as measured rows on the existing publication surface; and
  - keep this slice distinct from the adjacent broader `{1,4}` backtracking-heavy and broader-range open-ended branch-local-backreference callable slices instead of inventing another benchmark family, detached helper, or bytes-only owner path.
- Focused and combined benchmark publications move honestly:
  - `nested-group-callable-replacement-boundary` moves from `72` total workloads / `72` measured workloads / `0` known gaps to `76` / `76` / `0`;
  - the combined source-tree report moves from `763` total workloads / `763` measured workloads / `0` known gaps to `767` / `767` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the four new broader-range open-ended `{2,}` backtracking-heavy callable rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_callable_replacement_parity_suite.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_callable_replacement_boundary.py --report .rebar/tmp/rbr-0696-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0694`; do not add new callable-replacement execution semantics here.
- Reuse the existing `nested_group_callable_replacement_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family, manifest, or detached promotion helper.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding callable slice is supposed to live behind `rebar._rebar`.
- Do not broaden into replacement-template flows, bytes mirrors, deeper grouped execution, another grouped family, or native-path benchmark publication in this run.

## Notes
- `RBR-0696` is the next available feature task id in the current checkout; `RBR-0695` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly behind the drained `RBR-0694` head so the broader-range open-ended `{2,}` nested backtracking-heavy callable slice reaches the existing Python-path benchmark surface before bytes mirrors or another grouped callable frontier reopen correctness work on this family.
- 2026-03-19 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0694-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-parity.md` records that the exact `str` pair now matches CPython through `rebar._rebar`, so benchmark catch-up is the adjacent bounded follow-on rather than another correctness publication or parity pass;
  - `benchmarks/workloads/nested_group_callable_replacement_boundary.py` currently contains the adjacent broader `{1,4}` backtracking-heavy callable rows on this same manifest, but direct `rg` probes found no workload ids or patterns for `a(((bc|b)c){2,})d` or `a(?P<outer>(?:(?P<inner>bc|b)c){2,})d`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently promotes the broader `{1,4}` backtracking-heavy callable slice as `nested-broader-range-backtracking-heavy-callable-replacement`, with no separate broader-range open-ended `{2,}` backtracking-heavy callable slice yet tracked on that owner surface; and
  - `reports/benchmarks/latest.py` currently publishes `nested-group-callable-replacement-boundary` at `72` total workloads / `72` measured workloads / `0` known gaps and the combined source-tree report at `763` / `763` / `0`, so this task is not a stale no-op.
