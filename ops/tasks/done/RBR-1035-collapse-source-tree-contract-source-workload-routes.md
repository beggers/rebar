## RBR-1035: Collapse source-tree contract source-workload routes

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining parallel source-workload selection and drift-check routes from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern success-owner contracts, wrong-text-model contracts, and compiled-pattern `module.compile` contracts all derive their source workloads through one canonical same-file helper path instead of three near-identical loops.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these duplicated source-workload helper routes:
  - `def _compiled_pattern_module_contract_source_workloads(...)`
  - `def _wrong_text_model_source_workloads(...)`
  - `def _wrong_text_model_source_workload_params(...)`
- Replace those detached routes with one canonical same-file source-workload selection path, or an equivalently smaller same-file structure, that is reused by all three existing benchmark-contract surfaces without adding a support module, registry file, or checked-in data layer:
  - the compiled-pattern success-owner path rooted at `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - the wrong-text-model owner path rooted at `WRONG_TEXT_MODEL_OWNER_SPECS`
  - `CompiledPatternModuleCompileContractCase.source_workloads()`
- Keep the current owner-specific semantics intact while sharing the source-workload route:
  - compiled-pattern success-owner surfaces still select workloads in the same `include_workload_selectors` order from the same `manifest_path`, still expect the same `expected_source_workload_ids`, and still raise the same `"compiled-pattern module contract source workloads drifted from the {case_id} owner-spec surface"` drift message when the live surface changes;
  - wrong-text-model surfaces still select workloads in the same `include_workload_selectors` order from the same `manifest_path`, still expect the same `owner_spec.expected_source_workload_ids`, and still raise the same `"wrong-text-model contract source workloads drifted from the {case_id} owner-spec surface"` drift message when the live surface changes;
  - `CompiledPatternModuleCompileContractCase.source_workloads()` still derives its expected source-workload ids from `expected_anchor_pairs`, still keeps the same selector order, and still preserves the current `"success"` versus `"keyword"` contract-surface wording in its drift error.
- Preserve the current paramization and verification surfaces that depend on those routes:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads`
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing`
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads`
  - `test_wrong_text_model_callbacks_preserve_precompile_contract`
- Keep the cleanup structural and bounded:
  - do not widen into `_source_tree_contract_manifest_payload(...)`, `_source_tree_contract_workload(...)`, `_source_tree_contract_manifest(...)`, workload manifests under `benchmarks/workloads/`, or harness code under `python/rebar_harness/`;
  - do not edit README/current-status/backlog prose, reports, or implementation code.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success or compiled_pattern_module_compile_success_and_keyword_contract or wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or wrong_text_model_rows_until_helper_invocation'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_contract_source_workloads\\(|def _wrong_text_model_source_workloads\\(|def _wrong_text_model_source_workload_params\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting duplicate source-workload plumbing over adding another detached abstraction layer.

## Notes
- `RBR-1035` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1035|RBR-1036|RBR-1037|RBR-1038|RBR-1039|RBR-1040" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `ops/tasks/done/` currently ends at `RBR-1034-publish-pattern-sub-str-repeated-count-one-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently defines `_compiled_pattern_module_contract_source_workloads(...)` at line `16565`, `CompiledPatternModuleCompileContractCase.source_workloads()` at line `16943`, `_wrong_text_model_source_workloads(...)` at line `17749`, and `_wrong_text_model_source_workload_params()` at line `17920`;
  - the targeted pytest slice in Verification currently passes (`150 passed, 570 deselected in 0.28s`); and
  - the negative `rg` check in Verification currently fails only because those exact duplicated source-workload helper names are still present.

## Completion
- 2026-03-23: Replaced the duplicated source-workload selection loops with one local `_contract_source_workloads(...)` helper, moved the compiled-pattern success-owner and wrong-text-model owner routes onto `source_workloads()` methods, and kept `CompiledPatternModuleCompileContractCase.source_workloads()` on the same selector order and drift wording through that shared helper.
- 2026-03-23: Reused one local `_contract_source_workload_params(...)` path for the affected parametrized tests and updated the remaining wrong-text-model anchor and haystack-text-model validation call sites to use the owner-spec method route.
- 2026-03-23: Verification passed with `150 passed, 570 deselected` for the targeted pytest slice, and the negative `rg` check confirmed the removed helper definitions no longer exist in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
