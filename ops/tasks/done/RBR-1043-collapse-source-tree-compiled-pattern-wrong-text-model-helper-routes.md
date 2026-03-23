# RBR-1043: Collapse source-tree compiled-pattern wrong-text-model helper routes

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining detached compiled-pattern wrong-text-model callback and CPython-dispatch helpers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern wrong-text-model owner specs derive that behavior through one canonical same-file owner-spec route instead of three parallel free functions.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines these detached compiled-pattern wrong-text-model helpers:
  - `def _compiled_pattern_wrong_text_model_expected_callback_result(...)`
  - `def _compiled_pattern_wrong_text_model_expected_callback_call(...)`
  - `def _run_cpython_compiled_pattern_wrong_text_model_workload(...)`
- Replace those three helpers with one canonical same-file route on `WrongTextModelOwnerSpec`, or an equivalently smaller same-file structure, reused by both compiled-pattern wrong-text-model owner specs without adding a support module, registry file, or checked-in data layer:
  - `_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC`
- Keep the current compiled-pattern wrong-text-model callback semantics intact while moving them onto that owner-spec route:
  - `module.subn` rows still return `("module-result", 0)`;
  - `module.finditer` rows still return `["module-finditer-result"]`;
  - the remaining successful callback-result cases still return `"module-result"`;
  - `module.search`, `module.match`, and `module.fullmatch` still expect `(operation, haystack_payload(), 0, {})`;
  - `module.split` still expects `(operation, haystack_payload(), maxsplit_argument(), 0, {})`;
  - `module.findall` and `module.finditer` still expect `(operation, haystack_payload(), 0)`; and
  - `module.sub` and `module.subn` still expect `(operation, replacement_payload(), haystack_payload(), count_argument(), 0, {})`.
- Keep the current compiled-pattern wrong-text-model CPython-dispatch semantics intact while moving them onto that owner-spec route:
  - the route still compiles `re.compile(workload.pattern_payload(), workload.flags)` before dispatching the helper call;
  - `module.search`, `module.match`, and `module.fullmatch` still dispatch the compiled pattern plus `haystack_payload()` and `flags`;
  - `module.split` still dispatches the compiled pattern plus `haystack_payload()` and `maxsplit_argument()`;
  - `module.findall` still dispatches the compiled pattern plus `haystack_payload()` and `flags`;
  - `module.finditer` still dispatches the compiled pattern plus `haystack_payload()` and `flags`, and still materializes the iterator into a list; and
  - `module.sub` and `module.subn` still dispatch the compiled pattern plus `replacement_payload()`, `haystack_payload()`, and `count_argument()`.
- Update the existing wrong-text-model call sites to use that canonical route while preserving the current owner coverage and local behavior asserted by these tests:
  - `test_collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured`
  - `test_module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured`
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation`
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads`
  - `test_wrong_text_model_callbacks_preserve_precompile_contract`
  - `test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_expected_callback_result\\(|def _compiled_pattern_wrong_text_model_expected_callback_call\\(|def _run_cpython_compiled_pattern_wrong_text_model_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen into the pattern-owner wrong-text-model helper families, compiled-pattern success-owner helper routes, workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, or non-benchmark test files.
- Do not edit README/current-status/backlog prose, reports, or implementation code.

## Notes
- `RBR-1043` is the next available unreserved task id in the current checkout:
  - `ops/tasks/done/` currently ends at `RBR-1042-publish-module-sub-bytes-repeated-count-one-pair.md`; and
  - `rg -n "RBR-1043|RBR-1044|RBR-1045|RBR-1046|RBR-1047" ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The duplication target is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently defines `WrongTextModelOwnerSpec` at line `17551`, `_compiled_pattern_wrong_text_model_expected_callback_result(...)` at line `17606`, `_compiled_pattern_wrong_text_model_expected_callback_call(...)` at line `17616`, `_run_cpython_compiled_pattern_wrong_text_model_workload(...)` at line `17659`, `_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC` at line `17798`, and `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC` at line `17830`;
  - the targeted pytest slice in Verification currently passes (`51 passed, 670 deselected, 8 subtests passed in 0.48s`); and
  - the negative `rg` check in Verification currently fails only because those exact helper definitions are still present.

## Completion Note
- Folded the compiled-pattern wrong-text-model callback-result, callback-call, and CPython-dispatch behavior into `WrongTextModelOwnerSpec` methods, renamed the pattern-owner delegate fields to keep their existing local routes intact, and removed the three detached compiled-pattern helper functions from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Repointed `_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC` and `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_OWNER_SPEC` to the owner-spec route without widening into adjacent success-owner or pattern-owner helper families.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract or collection_replacement_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or module_boundary_manifest_keeps_compiled_pattern_wrong_text_model_rows_measured or standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
  - `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_expected_callback_result\\(|def _compiled_pattern_wrong_text_model_expected_callback_call\\(|def _run_cpython_compiled_pattern_wrong_text_model_workload\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
