# RBR-0714: Catch up the module-workflow multiline compile regression benchmark

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published Python-path regression benchmark surface with the exact `str` multiline-only module-compile row that `RBR-0712` just moved behind `rebar._rebar`, so this bounded compile family stays caught up on the existing `regression_matrix.py` path before another module-workflow follow-on reopens the frontier.

## Deliverables
- `benchmarks/workloads/regression_matrix.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `reports/benchmarks/latest.py`

## Acceptance Criteria
- `benchmarks/workloads/regression_matrix.py` remains the only benchmark manifest for this slice and grows by only one new workload:
  - add `regression-module-compile-multiline-purged` beside the existing verbose module-compile regression rows;
  - keep the exact multiline compile pattern anchored to the shared module-workflow regression spelling instead of inventing another compile family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 8`;
    - `text_model == "str"`;
    - `operation == "module.compile"`;
    - `cache_mode == "purged"`; and
    - `timing_scope == "module-helper-call"`;
  - keep this row multiline-only rather than verbose or bytes-backed; and
  - do not broaden into a bytes multiline sibling, warm/cold cache variants, search/match execution, or another regression manifest.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps this work on the existing shared benchmark-contract path instead of forking a multiline-only benchmark suite:
  - update the regression-manifest workload/scorecard expectations from `6` measured workloads to `7`, with `0` known gaps still required on the shared source-tree benchmark surface;
  - update the standard compile-proxy anchor mapping so `regression-module-compile-multiline-purged` is pinned to the already-published correctness case id `workflow-compile-str-multiline-regression`; and
  - keep the regression pack on the existing `regression-pack-full` path, with the new multiline workload visible in the measured regression surface instead of creating another scoped pack or detached expectation helper.
- `reports/benchmarks/latest.py` is regenerated honestly:
  - the combined benchmark publication moves from `772` total / `772` measured / `0` known gaps across `30` manifests to `773` / `773` / `0` across the same `30` manifests;
  - `REPORT["summary"]["module_workloads"]` moves from `764` to `765`, and `REPORT["summary"]["regression_workloads"]` moves from `6` to `7`;
  - `REPORT["manifests"]["regression-matrix"]` moves from `6` selected / `6` measured / `0` known gaps to `7` / `7` / `0`; and
  - the new workload is published as `measured`, not silently omitted.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0714-regression-matrix.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`

## Constraints
- Keep this task benchmark-only. Do not widen the correctness surface, add bytes multiline compile support, or change the Rust/Python implementation just to support a larger benchmark family.
- Reuse the existing `regression_matrix.py` manifest and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` owner path. Do not create another multiline-only benchmark manifest, another benchmark suite, or a detached benchmark expectation helper in this run.
- Keep the benchmark comparison on the Python-facing source-tree shim path used by the tracked publication.

## Notes
- `RBR-0714` is the next available feature task id in the current checkout; `rg -n "RBR-0714" ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked ops/state/backlog.md ops/state/current_status.md` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0712` head so the newly landed multiline compile parity slice reaches the existing regression benchmark surface before another module-workflow correctness follow-on broadens the same family.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0712-module-workflow-multiline-compile-parity.md` explicitly keeps later benchmark catch-up for this exact multiline compile family on `benchmarks/workloads/regression_matrix.py`;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(pattern, rebar.MULTILINE) ... PY` now succeeds for the exact shared regression pattern, returning a `rebar.Pattern` with `flags == 40`, `groups == 1`, and `groupindex == {"key": 1}`;
  - `reports/benchmarks/latest.py` currently reports `772` total / `772` measured / `0` known gaps overall, with `REPORT["summary"]["module_workloads"] == 764` and `REPORT["summary"]["regression_workloads"] == 6`;
  - `reports/benchmarks/latest.py` does not yet publish any `regression-module-compile-multiline-purged` row; and
  - the adjacent bytes sibling stays out of scope for this task because `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(bytes_pattern, rebar.MULTILINE) ... PY` still raises `NotImplementedError`, so the next bounded benchmark catch-up here is the newly landed `str` multiline row, not a broader bytes expansion.

## Completion
- 2026-03-19: Added the exact `regression-module-compile-multiline-purged` workload to the existing `regression_matrix.py` manifest, kept it on the shared compile-proxy anchor path via `workflow-compile-str-multiline-regression`, and updated the shared source-tree benchmark-contract expectations without creating a new manifest or suite.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --manifest benchmarks/workloads/regression_matrix.py --report .rebar/tmp/rbr-0714-regression-matrix.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.benchmarks --report reports/benchmarks/latest.py`.
- Verified the tracked `reports/benchmarks/latest.py` diff before closing the task. The published combined benchmark scorecard now reads `773` total / `773` measured / `0` known gaps across `30` manifests, with `REPORT["summary"]["module_workloads"] == 765`, `REPORT["summary"]["regression_workloads"] == 7`, and `REPORT["manifests"]["regression-matrix"]` at `7` selected / `7` measured / `0` known gaps; the new `regression-module-compile-multiline-purged` row is published as `measured`.
