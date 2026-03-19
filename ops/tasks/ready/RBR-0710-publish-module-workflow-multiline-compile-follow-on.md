# RBR-0710: Publish the module-workflow multiline compile follow-on

Status: ready
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Reopen the module-workflow correctness frontier with the exact `rebar.compile(pattern, rebar.MULTILINE)` neighbor gap that `RBR-0706` intentionally left pinned, so the next bounded slice stays on the existing module-workflow compile owner path before any later Rust-backed parity or benchmark catch-up broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new compile row:
  - add `workflow-compile-str-multiline-regression` beside the existing verbose regression rows;
  - keep the exact compile pattern pair anchored to the current shared module-workflow regression spelling instead of inventing another pattern family:
    - the existing neighbor row `workflow-compile-str-verbose-regression` keeps `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`, `flags == 72`, and `text_model == "str"`; and
    - the new follow-on row uses that same `str` pattern with `flags == 8` (`MULTILINE`) and no `VERBOSE`;
  - do not broaden into bytes siblings, cache-state variants, search/match execution, or another compile family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking a multiline-only suite:
  - update the bundle-contract expectations, ordered compile-case inventory, pattern inventory, and operation/helper counts so `module-workflow-surface` now publishes six compile rows instead of five, with the new multiline row explicit in the shared compile selection;
  - keep `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()` honest for the exact public call `rebar.compile(pattern, rebar.MULTILINE)`: if live `rebar` still raises `NotImplementedError`, preserve that explicit pinned gap instead of forcing the source-package assertion to pretend the multiline variant already works; and
  - do not fork another manifest owner, another parity suite, or a detached multiline-only helper path for this one follow-on row.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1383` total / `1383` passed / `0` `unimplemented` across `114` manifests to `1384` total across the same `114` manifests, with the new multiline compile row reported as either `pass` or `unimplemented` according to the live `rebar` result;
  - `module.workflow` moves from `13` total / `13` passed / `0` `unimplemented` to `14` total, with the new multiline row reflected in the published suite summary;
  - `module.workflow.compile` moves from `5` total / `5` passed / `0` `unimplemented` to `6` total; and
  - the new row is not dropped from the scorecard even if live `rebar` still reports it as unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0710-module-workflow-multiline.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement the multiline compile behavior in Rust or Python just to make the new row pass.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another fixture, another parity suite, or a detached benchmark manifest in this run.
- Keep any later parity follow-on on the existing module-workflow parity path, and keep any later benchmark catch-up for this exact compile family on the existing `benchmarks/workloads/regression_matrix.py` path.

## Notes
- `RBR-0710` is the next available feature task id in the current checkout; `RBR-0709` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0710" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned no matches during this planning run.
- Queue this directly behind the drained `RBR-0708` feature head so the module-workflow compile frontier reopens through the exact pinned neighbor gap on the shared correctness path instead of switching to a new family while this compile owner is still locally anchored.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0706-module-workflow-verbose-bytes-compile-parity.md` explicitly kept the adjacent `rebar.compile(pattern, rebar.MULTILINE)` call pinned as unsupported inside `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()`;
  - `tests/python/test_module_workflow_parity_suite.py` still raises `NotImplementedError` for that exact call today, while the surrounding verbose `str` and `bytes` compile neighbors now pass through `rebar._rebar`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the shared verbose `str` and `bytes` compile rows but no multiline-only sibling on the same pattern family;
  - `reports/correctness/latest.py` currently reports `1383` total / `1383` passed / `0` `unimplemented` across `114` manifests, so reopening the frontier now has to come from an adjacent pinned gap rather than an already-published `unimplemented` row; and
  - `benchmarks/workloads/regression_matrix.py` already owns the adjacent verbose module-compile regression rows for this exact pattern family, so any later benchmark catch-up can stay on the shared regression manifest instead of inventing another compile surface.
