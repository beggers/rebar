# RBR-0431: Catch bounded two-arm conditional replacement-template benchmarks up with the new slice

Status: done
Owner: feature-implementation
Created: 2026-03-16
Completed: 2026-03-16

## Goal
- Refresh the published benchmark surface so the bounded two-arm conditional replacement-template workflow already live behind `rebar._rebar` produces a real Python-path timing on the existing `conditional_group_exists_boundary.py` manifest instead of lingering as the last explicit known-gap anchor on that boundary.

## Deliverables
- `benchmarks/workloads/conditional_group_exists_boundary.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- The existing `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap` anchor on `benchmarks/workloads/conditional_group_exists_boundary.py` is converted into a real `rebar` timing for the bounded numbered `module.sub()` replacement-template helper path already defined on that manifest, without widening into named or compiled-template benchmark expansion yet.
- `reports/benchmarks/latest.py` records a real `rebar` timing for that workload and no longer reports an explicit known gap on `conditional-group-exists-boundary`, while preserving the current source-tree-shim publication path and the overall combined-report structure.
- The shared benchmark expectations in `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stay on the consolidated source-tree benchmark surfaces, reflect `conditional-group-exists-boundary` moving to `known_gap_count: 0`, and preserve the combined-suite counts implied by the refreshed report.
- Verification passes with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0431-conditional-template-bench.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.

## Constraints
- Keep this task scoped to benchmark catch-up for behavior already implemented by `RBR-0430`; do not add new regex or replacement-template semantics here.
- Reuse the existing benchmark adapter/provenance machinery and consolidated source-tree benchmark assertions instead of reviving manifest-specific benchmark tests.
- Do not silently benchmark Python-only fallback behavior if the corresponding replacement-template slice is supposed to live behind `rebar._rebar`.
- Leave any remaining absent-capture or named compiled-`Pattern` template benchmark expansion for follow-on planning work.

## Notes
- Build on `RBR-0430`, `RBR-0426`, `RBR-0424`, and the existing `conditional_group_exists_boundary.py` benchmark surface.
- The tracked benchmark report currently shows `conditional-group-exists-boundary` at `53` workloads, `52` measured workloads, and `1` known gap; the remaining gap is `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap`.

## Completion
- Refreshed `benchmarks/workloads/conditional_group_exists_boundary.py` so the existing `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap` anchor is described as a former gap anchor rather than an unsupported row, and updated the manifest-level note to record the newly measured numbered `module.sub()` `\\1` replacement-template helper while keeping the remaining absent-capture and named compiled-entrypoint template expansion for follow-on work.
- Updated the shared source-tree benchmark expectations in `tests/benchmarks/benchmark_expectations.py` so `conditional-group-exists-boundary` now expects `known_gap_count: 0`, treats the former template anchor as a representative measured workload, and lets the combined-suite summary drop by one known gap everywhere that manifest participates.
- Republished `reports/benchmarks/latest.py`. The tracked benchmark scorecard now reports `565` total workloads, `543` measured workloads, and `22` known gaps overall; within `conditional-group-exists-boundary`, the tracked publication now reports `53` workloads, `53` measured workloads, and `0` known gaps, and `module-sub-template-numbered-conditional-group-exists-replacement-warm-gap` is recorded as a measured `rebar` timing.
- Remaining follow-on scope stays with `RBR-0433`: absent-capture numbered `module.subn()` plus named compiled-`Pattern` `sub()` / `subn()` replacement-template timings on this benchmark boundary.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_python_benchmark_manifest_contract.py tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` (`9 passed, 311 subtests passed`)
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/conditional_group_exists_boundary.py --report .rebar/tmp/rbr-0431-conditional-template-bench.py` (`{"known_gap_count": 0, "measured_workloads": 53, "module_workloads": 53, "parser_workloads": 0, "regression_workloads": 0, "total_workloads": 53}`)
- `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py` (`{"known_gap_count": 22, "measured_workloads": 543, "module_workloads": 557, "parser_workloads": 8, "regression_workloads": 5, "total_workloads": 565}`)
