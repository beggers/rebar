# RBR-0708: Catch up the module-workflow verbose bytes compile regression benchmark

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published Python-path regression benchmark surface with the exact `bytes` sibling of the already-measured verbose module-compile regression row, so the module-workflow verbose compile family stays caught up on the existing `regression_matrix.py` path now that `RBR-0706` moved the bytes case behind `rebar._rebar`.

## Deliverables
- `benchmarks/workloads/regression_matrix.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/regression_matrix.py` remains the only benchmark manifest for this slice and grows by only one new workload:
  - add `regression-module-compile-verbose-purged-bytes` beside the existing `regression-module-compile-verbose-purged`;
  - keep the exact verbose compile pattern pair anchored to the shared module-workflow regression spelling instead of inventing another compile family:
    - `^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $` with `text_model == "str"` for the already-measured row; and
    - the same pattern with `text_model == "bytes"` for the new follow-on row;
  - keep `operation == "module.compile"`, `flags == 72`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"` on the new row; and
  - do not broaden into warm/cold cache variants, search/match execution, additional verbose workflows, or another regression manifest.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing shared benchmark-contract path instead of forking a bytes-only benchmark suite:
  - update the regression-manifest workload/scorecard expectations from `5` measured workloads to `6`, with `0` known gaps still required on the shared source-tree benchmark surface;
  - update the standard compile-proxy anchor mapping so `regression-module-compile-verbose-purged-bytes` stays pinned to the already-published correctness case id `workflow-compile-bytes-verbose-regression` beside the existing `workflow-compile-str-verbose-regression` row; and
  - keep the regression pack on the existing `regression-pack-full` path, with the new bytes verbose workload visible in the measured regression surface instead of creating another scoped pack or detached expectation helper.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - the combined benchmark publication moves from `771` total / `771` measured / `0` known gaps across `30` manifests to `772` / `772` / `0` across the same `30` manifests;
  - `REPORT["summary"]["module_workloads"]` moves from `763` to `764`, and `REPORT["summary"]["regression_workloads"]` moves from `5` to `6`;
  - `REPORT["manifests"]["regression-matrix"]` moves from `5` selected / `5` measured / `0` known gaps to `6` / `6` / `0`; and
  - the new workload is published as `measured`, not silently omitted.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0708-regression-matrix.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add more module-workflow verbose compile behavior, or change the Rust/Python implementation just to support a larger benchmark family.
- Reuse the existing `regression_matrix.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another bytes-only benchmark manifest, another benchmark suite, or a detached benchmark expectation helper in this run.
- Keep the benchmark comparison on the Python-facing source-tree shim path used by the tracked publication.

## Notes
- `RBR-0708` is the next available feature task id in the current checkout; `RBR-0707` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `RBR-0708` had no matches in `ops/tasks/ready`, `ops/tasks/in_progress`, `ops/tasks/done`, `ops/tasks/blocked`, `ops/state/backlog.md`, or `ops/state/current_status.md` during this planning run.
- Queue this directly behind the drained `RBR-0706` head so the newly landed bytes verbose compile parity slice reaches the existing regression benchmark surface before another module-workflow follow-on or a broader regression expansion reopens the frontier.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0706-module-workflow-verbose-bytes-compile-parity.md` records that the exact verbose `bytes` compile pair now matches CPython through `rebar._rebar` and explicitly leaves later benchmark catch-up on `benchmarks/workloads/regression_matrix.py`;
  - `benchmarks/workloads/regression_matrix.py` currently carries only the `str` row `regression-module-compile-verbose-purged` for this verbose compile family, alongside the neighboring regression import/parser/bytes-search probes;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently anchors only `regression-module-compile-verbose-purged` to `workflow-compile-str-verbose-regression` and still expects the regression manifest to stay at `5` measured workloads;
  - `reports/benchmarks/latest.py` currently reports `771` total / `771` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 763`, `REPORT["summary"]["regression_workloads"] == 5`, and `REPORT["manifests"]["regression-matrix"]["measured_workloads"] == 5`; and
  - `tests/conformance/fixtures/module_workflow_surface.py` plus `tests/python/test_module_workflow_parity_suite.py` already publish and exercise the exact correctness anchor `workflow-compile-bytes-verbose-regression`, so this benchmark task can stay on the existing shared regression manifest instead of inventing another benchmark family.
