## RBR-1039: Collapse source-tree compiled-pattern expected-build-call helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining parallel compiled-pattern expected-build-call helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern keyword, success, wrong-text-model, and `module.compile` contract surfaces all derive their precompile/purge call expectations through one canonical same-file route instead of three near-identical free functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached helpers:
  - `def _compiled_pattern_module_helper_contract_expected_build_calls(...)`
  - `def _compiled_pattern_module_contract_expected_build_calls(...)`
  - `def _compiled_pattern_module_compile_contract_expected_build_calls(...)`
- Replace those three helpers with one canonical same-file expected-build-call route, or an equivalently smaller same-file structure, reused by the existing compiled-pattern contract carriers without adding a support module, registry file, or checked-in data layer:
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
  - `CompiledPatternModuleSuccessOwnerSpec`
  - the compiled-pattern `WrongTextModelOwnerSpec` entries in `WRONG_TEXT_MODEL_OWNER_SPECS`
  - `CompiledPatternModuleCompileContractCase`
- Keep the current build-call semantics intact while sharing the route:
  - every compiled-pattern contract path still expects the initial `("compile", source_workload.pattern_payload(), source_workload.flags)` call before timing;
  - `cache_mode == "warm"` still expects only that compile call;
  - `cache_mode == "purged"` still appends `("purge",)` after the compile call; and
  - unsupported cache modes still raise the current label-specific error wording for the helper-keyword, success/wrong-text-model, and `module.compile` contract surfaces.
- Update the existing callback/precompile assertion call sites to use that canonical route while preserving the current coverage and local behavior asserted by these tests:
  - `test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing`
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing`
  - `test_wrong_text_model_callbacks_preserve_precompile_contract`
- Keep the cleanup structural and bounded:
  - do not widen into the direct-`Pattern` wrong-text-model build-call helpers, callback-call/result helpers, payload round-trip helpers, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, or non-benchmark test files; and
  - do not edit README/current-status/backlog prose, reports, or implementation code.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing or wrong_text_model_callbacks_preserve_precompile_contract'`
- `bash -lc "! rg -n 'def _compiled_pattern_module_helper_contract_expected_build_calls\\(|def _compiled_pattern_module_contract_expected_build_calls\\(|def _compiled_pattern_module_compile_contract_expected_build_calls\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting duplicate expected-build-call plumbing over introducing another detached abstraction layer.

## Notes
- `RBR-1039` is the next available unreserved task id in the current checkout:
  - `rg -n "RBR-1039|RBR-1040|RBR-1041|RBR-1042|RBR-1043|RBR-1044" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `ops/tasks/done/` currently ends at `RBR-1038-publish-pattern-sub-bytes-repeated-count-one-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently defines `_compiled_pattern_module_helper_contract_expected_build_calls(...)` at line `16003`, `_compiled_pattern_module_contract_expected_build_calls(...)` at line `16630`, and `_compiled_pattern_module_compile_contract_expected_build_calls(...)` at line `17217`;
  - the targeted pytest slice in Verification currently passes (`56 passed, 665 deselected in 0.15s`); and
  - the negative `rg` check in Verification currently fails only because those exact helper definitions are still present.
