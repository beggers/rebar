## RBR-1041: Collapse source-tree compiled-pattern success callback helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached compiled-pattern success callback expectation helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the collection/replacement and module-boundary success owner specs derive their callback-call and callback-result expectations through one canonical owner-spec route instead of four parallel free functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached success callback helpers:
  - `def _compiled_pattern_module_collection_replacement_success_callback_result(...)`
  - `def _compiled_pattern_module_collection_replacement_success_callback_call(...)`
  - `def _compiled_pattern_module_boundary_success_callback_result(...)`
  - `def _compiled_pattern_module_boundary_success_callback_call(...)`
- Replace those four helpers with one canonical same-file callback-expectation route on `CompiledPatternModuleSuccessOwnerSpec`, or an equivalently smaller file-local structure, without adding a support module, registry file, or checked-in data layer.
- Keep the current callback semantics intact while moving them onto the owner-spec route:
  - collection/replacement success rows still return `("module-result", 0)` for `module.subn`, still return `["module-finditer-result"]` for `module.finditer`, and still return `"module-result"` for the remaining successful collection/replacement helper cases;
  - collection/replacement success rows still expect the same callback-call tuples for `module.split`, `module.findall`, `module.finditer`, `module.sub`, and `module.subn`, including the current `maxsplit_argument()`, `count_argument()`, `flags`, and `{}` kwargs placements;
  - module-boundary success rows still return `"module-result"` and still expect the same callback-call tuples for `module.search`, `module.match`, and `module.fullmatch`, with the current `(haystack_payload(), 0, {})` argument shape.
- Update the existing call sites to use that canonical route while preserving the current success-owner coverage and local behavior asserted by these tests:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads`
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing`
  - `test_compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases`
- Keep the cleanup structural and bounded:
  - do not widen into `_compiled_pattern_module_helper_contract_expected_callback_call(...)`, `_compiled_pattern_module_helper_contract_expected_callback_result(...)`, wrong-text-model callback helpers, compiled-pattern `module.compile` callback assertions, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, or non-benchmark test files; and
  - do not edit README/current-status/backlog prose, reports, or implementation code.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_collection_replacement_success_callback_result\\(|def _compiled_pattern_module_collection_replacement_success_callback_call\\(|def _compiled_pattern_module_boundary_success_callback_result\\(|def _compiled_pattern_module_boundary_success_callback_call\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting detached success callback helper plumbing over introducing another abstraction layer.

## Notes
- `RBR-1041` is the next available unreserved task id in the current checkout:
  - `ops/tasks/done/` currently ends at `RBR-1040-catch-up-pattern-sub-bytes-repeated-count-one-pair.md`; and
  - `rg -n 'RBR-1041|RBR-1042|RBR-1043|RBR-1044|RBR-1045' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently defines `_compiled_pattern_module_collection_replacement_success_callback_result(...)` at line `16446`, `_compiled_pattern_module_collection_replacement_success_callback_call(...)` at line `16456`, `_compiled_pattern_module_boundary_success_callback_result(...)` at line `16488`, and `_compiled_pattern_module_boundary_success_callback_call(...)` at line `16494`;
  - the targeted pytest slice in Verification currently passes (`42 passed, 679 deselected in 0.19s`); and
  - the negative `rg` check in Verification currently fails only because those exact helper definitions are still present.

## Completion
- 2026-03-23: Collapsed the four detached compiled-pattern success callback helpers into `CompiledPatternModuleSuccessOwnerSpec.expected_callback_result(...)` and `.expected_callback_call(...)`, keeping the collection/replacement and module-boundary callback semantics unchanged while removing the redundant free-function route. Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_boundary_verbose_bytes_success_rows_stay_anchored_to_published_correctness_cases'` (`42 passed, 679 deselected`) and `bash -lc \"! rg -n 'def _compiled_pattern_module_collection_replacement_success_callback_result\\(|def _compiled_pattern_module_collection_replacement_success_callback_call\\(|def _compiled_pattern_module_boundary_success_callback_result\\(|def _compiled_pattern_module_boundary_success_callback_call\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py\"`.
