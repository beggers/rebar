# RBR-0456: Collapse the last manual source-tree scorecard cases onto derived expectations

Status: ready
Owner: architecture-implementation
Created: 2026-03-16

## Goal
- Remove the last hand-maintained source-tree benchmark scorecard bookkeeping in `tests/benchmarks/benchmark_expectations.py` so `compile-smoke` and `regression-pack-smoke` derive their shared case shape from live manifest data and selected workloads instead of carrying static summary and manifest-count copies.

## Deliverables
- `tests/benchmarks/benchmark_expectations.py`
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`

## Acceptance Criteria
- `tests/benchmarks/benchmark_expectations.py` gains one small helper or extends the existing source-tree case resolver so the two remaining manual source-tree scorecard cases are resolved through the same live manifest-loading path already used by `source_tree_scorecard_case(...)`.
- The cleanup is scoped to exactly these cases:
  - `compile-smoke`
  - `regression-pack-smoke`
- After the refactor, those two case definitions no longer open-code the shared bookkeeping that the file can derive:
  - `manifest_ids`
  - `selection_mode`
  - `expected_summary`
  - one-entry `manifest_expectations` blocks whose only payload is `known_gap_count`
- The derived summary for `regression-pack-smoke` is computed from the smoke-selected workload rows, not from the full `regression-matrix` manifest totals.
- Keep the intentionally case-local frontier explicit where it is narrower than the derived shared metadata:
  - `compile-smoke` still keeps its current `expected_first_deferred`, `representative_measured_workload_ids`, and `representative_known_gap_workload_ids`.
  - `regression-pack-smoke` still keeps its current `expected_workload_order`, `representative_measured_workload_ids`, and `representative_known_gap_workload_ids`.
- Keep known-gap metadata single-sourced where possible:
  - `regression-pack-smoke` reuses the current `regression-matrix` known-gap count from `SOURCE_TREE_COMBINED_MANIFEST_EXPECTATIONS`.
  - `compile-smoke` may keep a tiny case-local known-gap scalar or equivalent because its provenance manifest is outside the published full-suite expectation map, but it must not keep a second hand-maintained summary dict.
- `source_tree_scorecard_case(...)` keeps the same returned public case shape consumed by `tests/benchmarks/test_source_tree_benchmark_scorecards.py`; this task deletes duplicate structure rather than changing the test API.
- If `tests/benchmarks/test_source_tree_benchmark_scorecards.py` needs edits, keep them limited to consuming the same case shape more directly. Do not add a second expectation registry in the test file.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_scorecards.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_adapter_provenance.py`.

## Constraints
- Prefer extending the existing `SOURCE_TREE_SCORECARD_EXPECTATIONS` resolver path and `expected_summary_for_manifests(...)` support over introducing another registry, support module, or generated data file.
- Keep the task scoped to benchmark expectation architecture. Do not change benchmark workload manifests, manifest selectors, harness adapter behavior, workload ids, or published reports to complete it.
- Preserve the current workload ordering and representative workload ids for the two scoped cases. The value of this task is deleting duplicate bookkeeping, not broadening or shrinking the published benchmark surface.

## Notes
- `RBR-0455` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned verbose `module.compile()` parity follow-on, so this architecture cleanup starts at `RBR-0456`.
- The runtime dashboard is current and clean (`Generated: 2026-03-16T07:32:22+00:00`, `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, no last-cycle anomalies), so rule 10 does not apply and this run should seed one post-JSON simplification task instead of no-oping.
- JSON counts are fully burned down in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- In the current checkout, `tests/benchmarks/benchmark_expectations.py` is still `1726` lines long, and the only remaining manual source-tree scorecard definitions are concentrated at:
  - `compile-smoke` (`tests/benchmarks/benchmark_expectations.py:54`)
  - `regression-pack-smoke` (`tests/benchmarks/benchmark_expectations.py:175`)
- `RBR-0452` and `RBR-0454` already collapsed all full source-tree scorecard cases onto shared manifest expectations and explicitly left these last standalone cases manual for a bounded follow-on.
