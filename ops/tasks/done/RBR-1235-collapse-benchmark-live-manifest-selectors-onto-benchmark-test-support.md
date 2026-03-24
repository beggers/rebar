## RBR-1235: Collapse benchmark live-manifest selectors onto benchmark test support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the duplicate live-manifest selector/cache layer from `tests/benchmarks/source_tree_benchmark_anchor_support.py` now that `tests/benchmarks/benchmark_test_support.py` already owns the neutral benchmark-manifest test helpers. The source-tree anchor module should stay focused on source-tree signature, anchoring, and CPython-result parity support instead of also owning generic manifest-loading selectors used by unrelated benchmark-support modules.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/benchmark_anchor_support_test_helpers.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/source_tree_contract_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`

## Acceptance Criteria
- Move the generic live-manifest workload selector ownership onto `tests/benchmarks/benchmark_test_support.py`:
  - add the cache-backed manifest-workload loader there;
  - add the filtered workload-selection helper there; and
  - make the helper names and signatures precise enough that downstream benchmark-support modules can import them directly without another bridge layer.
- Delete the duplicate selector/cache functions from `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - remove `_manifest_workloads(...)`; and
  - remove `_selected_manifest_workloads(...)`.
- Update downstream imports to use `tests/benchmarks/benchmark_test_support.py` directly for the moved manifest-selector helpers:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py`;
  - `tests/benchmarks/standard_benchmark_anchor_support.py`;
  - `tests/benchmarks/source_tree_contract_benchmark_support.py`;
  - `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py`;
  - `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Rehome the focused cache/selection coverage onto the neutral owner instead of leaving it stranded on the source-tree module:
  - extend `tests/benchmarks/test_benchmark_test_support.py` to cover the moved loader/selector behavior and cache reuse; and
  - trim `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it no longer acts as the primary owner test for the moved generic selector layer.
- Update `tests/benchmarks/benchmark_anchor_support_test_helpers.py` so the cache guard clears the moved benchmark-test-support cache instead of clearing a source-tree-owned cache that should no longer exist.
- Preserve current benchmark behavior exactly:
  - the anchored-workload resolution logic in `tests/benchmarks/source_tree_benchmark_anchor_support.py` must still produce the same workload ids and case mappings;
  - the contract builders in `tests/benchmarks/source_tree_contract_benchmark_support.py` and `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` must still draw the same source workloads in the same order; and
  - do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Constraints
- Keep the cleanup structural and bounded to the benchmark-support/test layer listed above. Do not modify workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops state prose.
- Prefer moving the existing selector/cache bodies onto `tests/benchmarks/benchmark_test_support.py` over introducing a new benchmark-support owner module.
- Preserve the current cache semantics, workload ordering, and manifest-path handling exactly.

## Notes
- `RBR-1235` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run;
  - the highest filed task is `RBR-1234`; and
  - `rg -n "RBR-1235|RBR-1236|RBR-1237|RBR-1238|RBR-1239" ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` matched only historical mentions inside completed task files, not a live reservation in tracked planning/state surfaces.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The live checkout still carries the duplicate manifest-selector ownership this task targets:
  - `tests/benchmarks/benchmark_test_support.py` already owns `_live_manifest_workloads_by_id(...)`, `live_manifest_workload(...)`, and `live_manifest_workloads(...)`; while
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still separately owns `_manifest_workloads(...)` and `_selected_manifest_workloads(...)`, and unrelated support modules import those source-tree-owned selectors directly.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` passed with `70 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `328 tests collected`.

## Completion Note
- Moved the cache-backed manifest tuple loader and filtered selector onto `tests/benchmarks/benchmark_test_support.py` as `manifest_workloads(...)` and `selected_manifest_workloads(...)`, rewired the benchmark-support and contract modules to import those helpers directly, trimmed the source-tree anchor support module back to anchoring-only responsibilities, and rehomed the cache/selector coverage onto `tests/benchmarks/test_benchmark_test_support.py`.
- Verification in this completion run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_contract_benchmark_support.py tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` passed with `72 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_standard_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `327 tests collected`.
