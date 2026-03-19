# RBR-0704: Publish the module-workflow verbose compile bytes follow-on

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Extend the published module-workflow correctness surface with the exact `bytes` sibling of the already-landed verbose compile regression case, so the frontier reopens on the tracked Python-facing correctness path before any Rust-backed parity or later benchmark catch-up broadens this compile workflow family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new compile row:
  - add `workflow-compile-bytes-verbose-regression` beside the existing `workflow-compile-str-verbose-regression`;
  - keep the exact verbose compile pattern pair anchored to the current shared regression spelling instead of inventing another pattern family:
    - `^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $` with `text_model == "str"` for the already-published row; and
    - the same pattern with `text_model == "bytes"` for the new follow-on row;
  - keep `flags == 72` (`MULTILINE | VERBOSE`) on the new row, and do not broaden into additional verbose workflows, cache-state variants, or non-verbose bytes compile cases.
- `tests/python/test_module_workflow_parity_suite.py` keeps the shared module-workflow owner aligned with the expanded manifest without forking another bytes-only suite:
  - update the bundle-contract expectations, compile-only case-id selection, pattern inventory, and operation/helper counts so `module-workflow-surface` now publishes five compile rows instead of four, with the new bytes verbose case explicit in the ordered fixture selection;
  - keep the existing six `VERBOSE_COMPILE_WORKFLOW_CASES` and their current `str` workflow texts unchanged in this publication task; and
  - keep `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()` honest for the exact bytes follow-on call `rebar.compile(pattern.encode("ascii"), int(VERBOSE_COMPILE_CASE.flags or 0))`: if live `rebar` still raises `NotImplementedError`, preserve that explicit pinned gap instead of forcing the source-package assertion to pretend the bytes variant already works.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1382` total / `1382` passed / `0` `unimplemented` across `114` manifests to `1383` total across the same `114` manifests, with the new bytes verbose compile row reported as either `pass` or `unimplemented` according to the live `rebar` result;
  - `module.workflow` moves from `12` total / `12` passed / `0` `unimplemented` to `13` total, with the new bytes compile row reflected in the published suite summary; and
  - the new row is not dropped from the scorecard even if live `rebar` still reports it as unimplemented.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0704-module-workflow-verbose-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not implement the bytes verbose compile behavior in Rust or Python just to make the new row pass.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another bytes-only fixture, another parity module, or another benchmark family in this run.
- Keep any later parity follow-on on the existing module-workflow parity path, and keep any later benchmark catch-up on the existing `benchmarks/workloads/regression_matrix.py` path.

## Notes
- `RBR-0704` is the next available feature task id in the current checkout; `RBR-0703` is already occupied by the done architecture cleanup task in `ops/tasks/done/`.
- Queue this directly after the drained `RBR-0702` head so the newly empty feature frontier reopens through one exact bytes compile publication follow-on on the existing module-workflow correctness path instead of stalling for another synthesis pass.
- 2026-03-19 feature-planning probes confirm this task is concrete from tracked frontier evidence:
  - `ops/tasks/done/RBR-0702-nested-broader-range-open-ended-backtracking-heavy-callable-replacement-bytes-benchmark-catch-up.md` records the latest feature frontier closing with the shared benchmark surface caught up and the ready queue drained, so the next bounded slice must come from another already-anchored parity gap rather than another callable benchmark expansion;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes `workflow-compile-str-verbose-regression` but has no `workflow-compile-bytes-verbose-regression` sibling;
  - `tests/python/test_module_workflow_parity_suite.py` currently pins the exact bytes follow-on `rebar.compile(pattern.encode("ascii"), int(VERBOSE_COMPILE_CASE.flags or 0))` as a `NotImplementedError` neighbor gap inside `test_source_package_verbose_compile_metadata_and_neighbor_gaps_remain_pinned()`;
  - `reports/correctness/latest.py` currently reports `1382` total / `1382` passed / `0` `unimplemented` across `114` manifests, and `module.workflow` at `12` total / `12` passed / `0` `unimplemented`, so this bytes verbose compile row is not yet represented on the tracked scorecard; and
  - `benchmarks/workloads/regression_matrix.py` already owns the adjacent `regression-module-compile-verbose-purged` `str` benchmark row, so any later Python-path benchmark catch-up for this same verbose compile family can stay on the existing regression manifest instead of inventing another benchmark surface.

## Completion
- 2026-03-19: Added `workflow-compile-bytes-verbose-regression` to the shared `module_workflow_surface.py` manifest, kept the shared module-workflow owner aligned with the new compile row, and preserved the explicit source-package gap where `rebar.compile(pattern.encode("ascii"), MULTILINE | VERBOSE)` still raises `NotImplementedError`.
- Republished `reports/correctness/latest.py`; the tracked combined scorecard now reports `1383` total / `1382` passed / `1` unimplemented across the same `114` manifests. `module.workflow` is now `13` total / `12` passed / `1` unimplemented, and both `module.workflow.bytes` and `module.workflow.compile` are `5` total / `4` passed / `1` unimplemented because the new bytes verbose compile row is published honestly as unimplemented.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0704-module-workflow-verbose-bytes.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
