# RBR-0716: Publish the module-workflow multiline bytes compile follow-on

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Reopen the module-workflow correctness frontier with the exact `rebar.compile(bytes_pattern, rebar.MULTILINE)` neighbor gap that `RBR-0714` intentionally left out, so the next bounded slice stays on the existing module-workflow compile owner path before later Rust-backed parity or benchmark catch-up broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new compile row:
  - add `workflow-compile-bytes-multiline-regression` beside the existing verbose and multiline regression rows;
  - keep the exact compile pattern anchored to the current shared module-workflow regression spelling instead of inventing another pattern family:
    - the existing neighbor row `workflow-compile-bytes-verbose-regression` keeps `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `flags == 72`, and `text_model == "bytes"`; and
    - the new follow-on row uses that same `bytes` pattern with `flags == 8` (`MULTILINE`) and no `VERBOSE`;
  - do not broaden into cache-state variants, search/match execution, extra bytes-only compile rows, or another compile family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking a bytes-only suite:
  - update the bundle-contract expectations, ordered compile-case inventory, pattern inventory, and operation/helper counts so `module-workflow-surface` now publishes seven compile rows instead of six, with the new bytes multiline row explicit in the shared compile selection;
  - keep the source-package regression-neighbor coverage honest for the exact public call `rebar.compile(bytes_pattern, rebar.MULTILINE)`: if live `rebar` still raises `NotImplementedError`, preserve that explicit pinned gap instead of forcing the source-package assertion to pretend the bytes multiline variant already works; and
  - do not fork another manifest owner, another parity suite, or a detached bytes-multiline helper path for this one follow-on row.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1384` total / `1384` passed / `0` `unimplemented` across `114` manifests to `1385` total across the same `114` manifests, with the new bytes multiline compile row reported as either `pass` or `unimplemented` according to the live `rebar` result;
  - `module.workflow` moves from `14` total / `14` passed / `0` `unimplemented` to `15` total, with the new bytes multiline row reflected in the published suite summary;
  - `module.workflow.compile` moves from `6` total / `6` passed / `0` `unimplemented` to `7` total; and
  - the new row is not dropped from the scorecard even if live `rebar` still reports it as unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0716-module-workflow-multiline-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement the bytes multiline compile behavior in Rust or Python just to make the new row pass.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another fixture, another parity suite, or a detached benchmark manifest in this run.
- Keep any later parity follow-on on the existing module-workflow parity path, and keep any later benchmark catch-up for this exact compile family on the existing `benchmarks/workloads/regression_matrix.py` path.

## Notes
- `RBR-0716` is the next available feature task id in the current checkout; `RBR-0715` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0716" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0714` feature head so the module-workflow compile frontier reopens through the exact unpublished bytes multiline neighbor on the shared correctness path instead of switching to a new family while this compile owner is still locally anchored.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0714-module-workflow-multiline-compile-benchmark-catch-up.md` explicitly left the bytes multiline sibling out of scope because `rebar.compile(bytes_pattern, rebar.MULTILINE)` still raised `NotImplementedError`;
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY' ... rebar.compile(bytes_pattern, rebar.MULTILINE) ... PY` on the current checkout still raises `NotImplementedError` with the scaffold placeholder message;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes `workflow-compile-str-multiline-regression` and `workflow-compile-bytes-verbose-regression` on the shared regression spelling but no `workflow-compile-bytes-multiline-regression` sibling;
  - `tests/python/test_module_workflow_parity_suite.py` currently tracks six compile rows on `module-workflow-surface`, with the regression-neighbor coverage anchored around the existing str multiline and bytes verbose cases but no published bytes multiline row;
  - `reports/correctness/latest.py` currently reports `1384` total / `1384` passed / `0` `unimplemented` across `114` manifests, so reopening the frontier now has to come from an adjacent unpublished row rather than an already-published honest gap; and
  - `benchmarks/workloads/regression_matrix.py` does not yet publish any `regression-module-compile-multiline-purged-bytes` row, so any later Python-path benchmark catch-up can stay on the shared regression manifest after this correctness-publication slice and its parity follow-on land.
