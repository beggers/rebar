# RBR-0605: Catch the quantified nested-group alternation branch-local-backreference bytes pair up on the benchmark surface

Status: done
Owner: feature-implementation
Created: 2026-03-18

## Goal
- Extend the published source-tree benchmark surface so the exact bounded quantified nested-group alternation branch-local-backreference bytes pair expected after `RBR-0603` produces real `rebar` timings on the existing nested-group alternation manifest.

## Deliverables
- `benchmarks/workloads/nested_group_alternation_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/nested_group_alternation_boundary.py` adds only these three bytes mirrors of the current quantified nested-group alternation branch-local-backreference `str` rows:
  - `module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-bytes`
  - `module-compile-named-quantified-nested-group-branch-local-backreference-warm-bytes`
  - `pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-bytes`
- The new rows stay pinned to the existing Python-path public patterns and haystacks for this exact bounded slice:
  - `rb"a((b|c)+)\\2d"` through `module.search(..., b"zzabbdzz")`;
  - `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"` through `module.compile(...)` and `Pattern.fullmatch(b"abccd")`.
- `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` treat the three new rows as measured source-tree workloads while keeping `nested-group-alternation-boundary` and the combined report at zero known gaps. Reuse the existing slice-derived representative path by widening the current `quantified-branch-local-backreference` slice and shared zero-gap expectation surface instead of inventing another benchmark family or a manifest-local bytes special case.
- Focused and combined benchmark publications move honestly:
  - `nested-group-alternation-boundary` moves from `22` total workloads / `22` measured workloads / `0` known gaps to `25` / `25` / `0`;
  - the combined source-tree report moves from `704` total workloads / `704` measured workloads / `0` known gaps to `707` / `707` / `0`.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes the three new branch-local-backreference bytes rows with `implementation_timing.status == "measured"` through the source-tree shim path; this task does not claim built-native full-suite publication.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report .rebar/tmp/rbr-0605-quantified-nested-group-alternation-branch-local-backreference-bytes-benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0603`; do not add new execution semantics here.
- Reuse the existing `nested_group_alternation_boundary.py` manifest path and the consolidated source-tree benchmark assertion surface instead of inventing another benchmark family or a bytes-only test path.
- Keep the measurements on the Python-facing `rebar` path; do not publish timings for Python-only fallback behavior if the corresponding correctness slice is supposed to live behind `rebar._rebar`.

## Notes
- Build on `RBR-0603`.
- 2026-03-18 feature-planning probes confirm this task is concrete from the tracked frontier:
  - `ops/tasks/ready/RBR-0603-quantified-nested-group-alternation-branch-local-backreference-bytes-parity.md` already pins the exact numbered and named bytes pair for `rb"a((b|c)+)\\2d"` and `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"`, and its notes already call for a later benchmark follow-on that mirrors the three adjacent `str` rows on the existing nested-group alternation benchmark surface;
  - `benchmarks/workloads/nested_group_alternation_boundary.py` currently contains the three quantified nested-group branch-local-backreference `str` workloads for this exact slice as `module-search-numbered-quantified-nested-group-branch-local-backreference-lower-bound-b-branch-warm-str`, `module-compile-named-quantified-nested-group-branch-local-backreference-warm-str`, and `pattern-fullmatch-named-quantified-nested-group-branch-local-backreference-repeated-mixed-purged-str`, and none of the planned `-bytes` mirrors;
  - `tests/benchmarks/benchmark_expectations.py` currently keeps `nested-group-alternation-boundary` on the shared slice-derived representative path, with the `quantified-branch-local-backreference` slice already owning the three adjacent `str` rows for this exact pair, so the follow-on can stay on the existing zero-gap assertion surface instead of inventing another bytes-specific benchmark contract;
  - `reports/benchmarks/latest.py` currently publishes `nested-group-alternation-boundary` at `22` total workloads / `22` measured workloads / `0` known gaps and the combined source-tree report at `704` / `704` / `0`; and
  - direct `PYTHONPATH=python ./.venv/bin/python` public-API probes from this planning run still raise `NotImplementedError` for both target bytes patterns at `rebar.compile(...)`, so this benchmark follow-on stays sequenced behind `RBR-0603` until parity lands.
- No further quantified nested-group branch-local-backreference bytes family should be queued ahead of this benchmark catch-up while the mixed `str`/`bytes` slice is still missing these source-tree benchmark mirrors.

## Completion Note
- 2026-03-18: Added the three bounded bytes mirrors on the existing `nested-group-alternation-boundary` manifest in `benchmarks/workloads/nested_group_alternation_boundary.py` for `rb"a((b|c)+)\\2d"` through `module.search(..., b"zzabbdzz")`, `rb"a(?P<outer>(?P<inner>b|c)+)(?P=inner)d"` through `module.compile(...)`, and `Pattern.fullmatch(b"abccd")`.
- Widened the shared `quantified-branch-local-backreference` slice in `tests/benchmarks/benchmark_expectations.py` so the existing slice-derived zero-gap representative path now treats the three new bytes rows as measured without adding a manifest-local override or a bytes-only benchmark family.
- Republished the tracked benchmark scorecard in `reports/benchmarks/latest.py`; the tracked artifact now shows `nested-group-alternation-boundary` at `25` total / `25` measured / `0` known gaps and the combined source-tree report at `707` total / `707` measured / `0` known gaps, with all three new bytes workload rows recorded as `implementation_timing.status == "measured"`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_branch_local_backreference_parity_suite.py -k quantified-nested-group-alternation-branch-local-backreference`, `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/nested_group_alternation_boundary.py --report .rebar/tmp/rbr-0605-quantified-nested-group-alternation-branch-local-backreference-bytes-benchmarks.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
