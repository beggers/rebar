# RBR-0720: Catch up the module-workflow multiline bytes compile regression benchmark

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published Python-path regression benchmark surface with the exact `bytes` sibling of the already-measured multiline module-compile regression row, so the module-workflow multiline compile family stays caught up on the existing `regression_matrix.py` path now that `RBR-0718` moved the bytes case behind `rebar._rebar`.

## Deliverables
- `benchmarks/workloads/regression_matrix.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/regression_matrix.py` remains the only benchmark manifest for this slice and grows by only one new workload:
  - add `regression-module-compile-multiline-purged-bytes` beside the existing `regression-module-compile-multiline-purged`;
  - keep the exact multiline compile pattern pair anchored to the shared module-workflow regression spelling instead of inventing another compile family:
    - `^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $` with `text_model == "str"` for the already-measured row; and
    - the same pattern with `text_model == "bytes"` for the new follow-on row;
  - keep `operation == "module.compile"`, `flags == 8`, `cache_mode == "purged"`, and `timing_scope == "module-helper-call"` on the new row; and
  - do not broaden into warm/cold cache variants, search/match execution, additional multiline workflows, or another regression manifest.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing shared benchmark-contract path instead of forking a bytes-only benchmark suite:
  - update the regression-manifest workload/scorecard expectations from `7` measured workloads to `8`, with `0` known gaps still required on the shared source-tree benchmark surface;
  - update the standard compile-proxy anchor mapping so `regression-module-compile-multiline-purged-bytes` stays pinned to the already-published correctness case id `workflow-compile-bytes-multiline-regression` beside the existing `workflow-compile-str-multiline-regression` row; and
  - keep the regression pack on the existing `regression-pack-full` path, with the new bytes multiline workload visible in the measured regression surface instead of creating another scoped pack or detached expectation helper.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - the combined benchmark publication moves from `773` total / `773` measured / `0` known gaps across `30` manifests to `774` / `774` / `0` across the same `30` manifests;
  - `REPORT["summary"]["module_workloads"]` moves from `765` to `766`, and `REPORT["summary"]["regression_workloads"]` moves from `7` to `8`;
  - `REPORT["manifests"]["regression-matrix"]` moves from `7` selected / `7` measured / `0` known gaps to `8` / `8` / `0`; and
  - the new workload is published as `measured`, not silently omitted.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0720-regression-matrix.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add more module-workflow multiline compile behavior, or change the Rust/Python implementation just to support a larger benchmark family.
- Reuse the existing `regression_matrix.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another bytes-only benchmark manifest, another benchmark suite, or a detached benchmark expectation helper in this run.
- Keep the benchmark comparison on the Python-facing source-tree shim path used by the tracked publication.

## Notes
- `RBR-0720` is the next available feature task id in the current checkout; `RBR-0719` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0720" ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked ops/state/backlog.md ops/state/current_status.md` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0718` head so the newly landed bytes multiline compile parity slice reaches the existing regression benchmark surface before another module-workflow follow-on or a broader regression expansion reopens the frontier.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0718-module-workflow-multiline-bytes-compile-parity.md` records that the exact bytes multiline compile pair now matches CPython through `rebar._rebar` and explicitly leaves later benchmark catch-up on `benchmarks/workloads/regression_matrix.py`;
  - `benchmarks/workloads/regression_matrix.py` currently carries `regression-module-compile-multiline-purged` for the shared multiline `str` row and `regression-module-compile-verbose-purged-bytes` for the adjacent bytes verbose neighbor, but no `regression-module-compile-multiline-purged-bytes` workload yet;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently anchors `regression-module-compile-multiline-purged` on the shared regression path and still expects the regression manifest to stay at `7` measured workloads;
  - `reports/benchmarks/latest.py` currently reports `773` total / `773` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 765`, `REPORT["summary"]["regression_workloads"] == 7`, and `REPORT["manifests"]["regression-matrix"]` at `7` selected / `7` measured / `0` known gaps; and
  - `tests/conformance/fixtures/module_workflow_surface.py` plus `tests/python/test_module_workflow_parity_suite.py` already publish and exercise the exact correctness anchor `workflow-compile-bytes-multiline-regression`, so this benchmark task can stay on the existing shared regression manifest instead of inventing another benchmark family.
