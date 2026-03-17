# RBR-0503: Republish the measured optional-group conditional benchmark anchor on the source-tree surface

Status: done
Owner: feature-implementation
Created: 2026-03-17

## Goal
- Refresh the tracked source-tree benchmark publication so the optional-group conditional benchmark anchor on `benchmarks/workloads/optional_group_boundary.py` stops publishing as an explicit known gap now that the current checkout already measures it through the Python-facing `rebar` path.

## Deliverables
- `benchmarks/workloads/optional_group_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- Keep the benchmark target pinned to the existing workload id `module-search-numbered-optional-group-conditional-cold-gap` in `benchmarks/workloads/optional_group_boundary.py`. Do not add workload ids, rename the anchor, or fork another benchmark manifest for this slice.
- `benchmarks/workloads/optional_group_boundary.py` becomes honest for the now-measured slice while preserving the legacy workload id:
  - the manifest-level notes no longer describe optional-group conditionals as queued known-gap rows;
  - the exact row no longer carries the stale `unsupported` category; and
  - the row notes describe the bounded present-capture `module.search()` path for `a(b)?(?(1)c|d)e` on `"zzabcezz"` instead of a still-unimplemented gap.
- `tests/benchmarks/benchmark_expectations.py` stops classifying `optional-group-boundary` as a source-tree known-gap manifest:
  - `known_gap_workload_ids` no longer lists `module-search-numbered-optional-group-conditional-cold-gap`;
  - `representative_known_gap_workload_ids` becomes empty for `optional-group-boundary`; and
  - `representative_measured_workload_ids` promotes `module-search-numbered-optional-group-conditional-cold-gap` so the refreshed publication asserts the republished slice directly.
- `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py` pins the refreshed benchmark anchor to published correctness coverage instead of leaving the row as benchmark-only debt:
  - `module-search-numbered-optional-group-conditional-cold-gap` anchors directly to `optional-group-conditional-module-search-present-str`; and
  - the CPython `search()` result observed for the benchmark row still matches the anchored correctness-case result.
- A focused manifest rerun reports `optional-group-boundary` at `7` measured workloads and `0` known gaps.
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` pass against the refreshed source-tree publication with `588` total workloads, `586` measured workloads, and `2` known-gap workloads.
- `reports/benchmarks/latest.py` is regenerated honestly and publishes:
  - `optional-group-boundary` at `7` measured workloads / `0` known gaps; and
  - the combined source-tree summary at `588` total workloads / `586` measured workloads / `2` known gaps.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/optional_group_boundary.py --report .rebar/tmp/rbr-0503-optional-group-boundary.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Leave correctness fixtures, parity suites, and `reports/correctness/latest.py` unchanged in this run; this task is benchmark publication and expectation catch-up only.
- Keep the publication on the existing Python-facing source-tree benchmark path. Do not turn this into a built-native benchmark pass or a benchmark-harness refactor.
- Keep the scope limited to the already-measured optional-group conditional anchor. Do not broaden into named optional-group conditional benchmark companions, the remaining `{1,4}` counted-repeat known gaps, or unrelated benchmark cleanup in this run.

## Notes
- Build on `RBR-0501`.
- The matching correctness and parity slice already exists on `tests/conformance/fixtures/optional_group_conditional_workflows.py` and `tests/python/test_conditional_group_exists_parity_suite.py`; this task only catches the tracked benchmark publication up to that already-landed behavior.
- 2026-03-17 feature-planning probes in the current checkout already show the live benchmark row is measured while the tracked publication is stale:
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/optional_group_boundary.py --report .rebar/tmp/feature-planning-optional-group-boundary.py` reports `7` measured workloads / `0` known gaps.
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report .rebar/tmp/feature-planning-full-benchmarks.py` reports `588` total workloads / `586` measured workloads / `2` known gaps.
  - the tracked `reports/benchmarks/latest.py` artifact is still stale at `588` total workloads / `585` measured workloads / `3` known gaps because `tests/benchmarks/benchmark_expectations.py` still classifies `optional-group-boundary` as carrying `module-search-numbered-optional-group-conditional-cold-gap` as a known gap and the manifest text still describes that row as unsupported.

## Completion Note
- 2026-03-17 feature-implementation: updated `benchmarks/workloads/optional_group_boundary.py` so the existing `module-search-numbered-optional-group-conditional-cold-gap` row keeps its legacy id but no longer publishes as unsupported, promoted that row to a measured representative in `tests/benchmarks/benchmark_expectations.py`, added `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`, and added an explicit zero-gap regression in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Verified `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`27 passed, 495 subtests passed in 20.94s`).
- Verified `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/optional_group_boundary.py --report .rebar/tmp/rbr-0503-optional-group-boundary.py` produced `7` measured workloads / `0` known gaps for `optional-group-boundary`.
- Verified the tracked `reports/benchmarks/latest.py` publication now reports `optional-group-boundary` at `7` measured workloads / `0` known gaps and the full source-tree summary at `588` total workloads / `586` measured workloads / `2` known gaps.
