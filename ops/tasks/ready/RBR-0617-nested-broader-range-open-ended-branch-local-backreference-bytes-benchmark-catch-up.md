# RBR-0617: Catch the nested broader-range open-ended branch-local-backreference bytes pair up on the benchmark surface

Status: ready
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact broader-range open-ended `{2,}` nested grouped-alternation branch-local-backreference bytes pair produces real `rebar` timings on the existing nested-group alternation manifest.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_alternation_boundary.py` adds only these three bytes mirrors of the current broader-range open-ended nested-group alternation branch-local-backreference `str` rows:
  - `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-bytes`
  - `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-bytes`
  - `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c){2,})\\2d"` through `module.search(..., b"zzabbbdzz")`;
  - `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"` through `module.compile(...)` and `Pattern.fullmatch(b"acccd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the three new rows as measured source-tree workloads while keeping `nested-group-alternation-boundary` and the combined report at zero known gaps. Reuse the existing slice-derived representative path by widening the current `broader-range-open-ended-branch-local-backreference` slice and shared zero-gap expectation surface instead of inventing another benchmark family or a manifest-local bytes special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-alternation-boundary` moves from `28` total workloads / `28` measured workloads / `0` known gaps to `31` / `31` / `0`;
  - the combined source-tree report moves from `710` total workloads / `710` measured workloads / `0` known gaps to `713` / `713` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the three new broader-range open-ended branch-local-backreference bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report .rebar/tmp/rbr-0617-nested-broader-range-open-ended-branch-local-backreference-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already targeted behind `rebar._rebar`; do not add new execution semantics here.
- Reuse the existing `nested_group_alternation_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only test path.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0615`.
- Queue this directly behind `RBR-0615` so the broader `{2,}` bytes pair reaches the same Python-path benchmark surface before the open-ended conditional branch-local-backreference bytes slice or deeper grouped execution broadens that family.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0615-nested-broader-range-open-ended-branch-local-backreference-bytes-parity.md` already pins the exact numbered and named bytes pair for `rb"a((b|c){2,})\\2d"` and `rb"a(?P<outer>(?P<inner>b|c){2,})(?P=inner)d"`, and its notes already call for a later benchmark follow-on that mirrors the three adjacent `str` rows on the existing nested-group alternation benchmark surface;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` currently contains the three broader-range open-ended nested-group branch-local-backreference `str` workloads for this exact slice as `module-search-numbered-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-b-branch-warm-str`, `module-compile-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-warm-str`, and `pattern-fullmatch-named-open-ended-quantified-nested-group-branch-local-backreference-broader-range-lower-bound-c-branch-purged-str`, and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` currently keeps `nested-group-alternation-boundary` on the shared `broader-range-open-ended-branch-local-backreference` slice, with the three adjacent `str` rows already registered for this exact pair, so the follow-on can stay on the existing zero-gap assertion surface instead of inventing another bytes-specific benchmark contract;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-alternation-boundary` at `28` total workloads / `28` measured workloads / `0` known gaps and the combined source-tree report at `710` / `710` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0615` until parity lands.
