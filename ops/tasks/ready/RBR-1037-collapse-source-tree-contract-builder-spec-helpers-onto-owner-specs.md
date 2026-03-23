## RBR-1037: Collapse source-tree contract builder-spec helpers onto owner specs

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached source-tree contract builder-spec and note helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern success-owner contracts, wrong-text-model contracts, and compiled-pattern `module.compile` contracts derive their own builder metadata from the existing owner-spec / contract-case objects instead of four parallel free functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached helper functions:
  - `def _compiled_pattern_module_contract_note(...)`
  - `def _compiled_pattern_module_success_contract_builder_spec(...)`
  - `def _wrong_text_model_contract_builder_spec(...)`
  - `def _compiled_pattern_module_compile_contract_builder_spec(...)`
- Replace those free functions with one canonical same-file builder-spec route on the existing contract carriers, or an equivalently smaller file-local structure, without adding a support module, registry file, or checked-in data layer:
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `WrongTextModelOwnerSpec`
  - `CompiledPatternModuleCompileContractCase`
- Keep the current builder-spec semantics intact while moving them onto the owner-spec / contract-case route:
  - compiled-pattern success-owner contracts still use `owner_spec.contract_manifest_id`, still keep `_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS`, still set `timing_scope="module-helper-call"`, and still emit the current `"successful"` note wording against `owner_spec.note_surface`;
  - wrong-text-model contracts still use `owner_spec.contract_manifest_id`, `owner_spec.excluded_fields`, `owner_spec.timing_scope`, and still emit no note when `owner_spec.note_surface is None`, while preserving the current `"wrong-text-model"` note wording when `note_surface` exists;
  - compiled-pattern `module.compile` contracts still use `manifest_id="module-boundary"`, still keep `contract_case.manifest_excluded_fields()`, still set `manifest_timed_samples=2`, still keep `timing_scope="module-helper-call"`, and still preserve the current split between the plain `module.compile` note and the `flags=` keyword note.
- Update all current call sites to use that canonical route while preserving the existing contract coverage and local behavior asserted by these tests:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads`
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing`
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads`
  - `test_wrong_text_model_callbacks_preserve_precompile_contract`
  - `test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases`
  - `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio`
  - `test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows`
- Keep the cleanup structural and bounded:
  - do not widen into `_contract_source_workloads(...)`, `_contract_source_workload_params(...)`, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, or non-benchmark test files;
  - do not edit README/current-status/backlog prose, reports, or implementation code.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_collection_replacement_success or compiled_pattern_module_boundary_success or compiled_pattern_module_compile_success_and_keyword_contract or wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or wrong_text_model_rows_until_helper_invocation or pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio or compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_success_contract_builder_spec\\(|def _wrong_text_model_contract_builder_spec\\(|def _compiled_pattern_module_compile_contract_builder_spec\\(|def _compiled_pattern_module_contract_note\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the detached builder-spec helpers over introducing another abstraction layer.

## Notes
- `RBR-1037` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1037|RBR-1038|RBR-1039|RBR-1040|RBR-1041|RBR-1042|RBR-1043|RBR-1044|RBR-1045" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `ops/tasks/done/` currently ends at `RBR-1036-catch-up-pattern-sub-str-repeated-count-one-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently defines `_compiled_pattern_module_contract_note(...)` at line `16551`, `_compiled_pattern_module_success_contract_builder_spec(...)` at line `16562`, `_wrong_text_model_contract_builder_spec(...)` at line `16601`, and `_compiled_pattern_module_compile_contract_builder_spec(...)` at line `17226`;
  - the targeted pytest slice in Verification currently passes (`158 passed, 562 deselected in 0.29s`); and
  - the negative `rg` check in Verification currently fails only because those exact helper definitions are still present.
