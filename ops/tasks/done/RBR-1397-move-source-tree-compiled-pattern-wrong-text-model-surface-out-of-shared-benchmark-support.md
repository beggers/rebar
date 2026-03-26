## RBR-1397: Move the source-tree compiled-pattern wrong-text-model surface out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-specific compiled-pattern wrong-text-model contract layer from `tests/benchmarks/benchmark_test_support.py`.
- Shared benchmark support still owns `_compiled_pattern_wrong_text_model_specs()`, `_compiled_pattern_wrong_text_model_source_workloads(...)`, `_run_cpython_compiled_pattern_module_helper_workload(...)`, `_assert_wrong_text_model_payload_round_trip(...)`, `_module_workflow_compiled_pattern_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_workload_signature(...)`, and `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)` even though the live contract specs already live in `tests/benchmarks/source_tree_benchmark_anchor_support.py` and the current callers are the source-tree owner tests, source-tree combined-suite tests, and benchmark-manifest validation coverage for those source-tree contract rows.
- Move that wrong-text-model family onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so `tests/benchmarks/benchmark_test_support.py` keeps only the genuinely shared compiled-pattern success and keyword-helper support layers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move `_compiled_pattern_wrong_text_model_specs()`, `_compiled_pattern_wrong_text_model_source_workloads(...)`, `_run_cpython_compiled_pattern_module_helper_workload(...)`, `_assert_wrong_text_model_payload_round_trip(...)`, `_module_workflow_compiled_pattern_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_workload_signature(...)`, and `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)` out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_benchmark_manifest_validation.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to consume that wrong-text-model helper family from the source-tree owner module instead of `benchmark_test_support`.
- Rewrite the ownership assertions in `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the wrong-text-model family is treated as source-tree-owned while the shared compiled-pattern success and keyword-helper surfaces remain shared-support-owned.
- If `tests/benchmarks/benchmark_test_support.py` still needs the moved selectors/signatures for `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, route that use through the source-tree owner module without re-exporting the moved names back through `benchmark_test_support.py`.
- Do not widen into the broader shared compiled-pattern success-owner-spec surface, keyword-helper contract surface, benchmark manifest rewrites, workload-id changes, or report changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio or run_cpython_compiled_pattern_module_helper_workload_materializes_finditer or module_workflow_compiled_pattern_correctness_case_signature_requires_compiled_module_call_shape'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_specs|def _compiled_pattern_wrong_text_model_source_workloads|def _run_cpython_compiled_pattern_module_helper_workload|def _assert_wrong_text_model_payload_round_trip|def _module_workflow_compiled_pattern_correctness_case_signature|def _module_workflow_compiled_pattern_workload_signature|def _is_module_workflow_compiled_pattern_wrong_text_model_workload' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the run bounded to this wrong-text-model owner-boundary cleanup. Do not widen into the larger shared compiled-pattern success-owner-spec family or the compiled-pattern keyword-helper contract family that still belong to `tests/benchmarks/benchmark_test_support.py`.
- Prefer moving the existing source-tree-specific helper family onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over creating another neutral helper module or another routed wrapper layer.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1397|RBR-1398|RBR-1399' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside completed task notes, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1397`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - I first checked the broader shared compiled-pattern support lane. The success-owner-spec and keyword-helper contract surfaces still span multiple suites and still read as genuinely shared support, so that is a larger follow-on rather than the smallest next owner-boundary cleanup.
  - I then checked the compiled-pattern wrong-text-model seam. `rg -n '_compiled_pattern_wrong_text_model_specs|_compiled_pattern_wrong_text_model_source_workloads|_run_cpython_compiled_pattern_module_helper_workload|_assert_wrong_text_model_payload_round_trip|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_wrong_text_model_workload' tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows the definitions still live in shared support while the contract specs already live in the source-tree owner module and the current consumers are source-tree-focused tests.
  - That makes the wrong-text-model family the next bounded cross-file simplification after the JSON burn-down: it deletes one remaining source-tree-specific layer from shared benchmark support without widening into the still-shared compiled-pattern success and keyword-helper machinery.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio or run_cpython_compiled_pattern_module_helper_workload_materializes_finditer or module_workflow_compiled_pattern_correctness_case_signature_requires_compiled_module_call_shape'` passed with `4 passed, 173 deselected in 0.18s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'` passed with `3 passed, 114 deselected in 0.14s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'` passed with `2 passed, 62 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'` passed with `6 passed, 273 deselected in 0.22s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_specs|def _compiled_pattern_wrong_text_model_source_workloads|def _run_cpython_compiled_pattern_module_helper_workload|def _assert_wrong_text_model_payload_round_trip|def _module_workflow_compiled_pattern_correctness_case_signature|def _module_workflow_compiled_pattern_workload_signature|def _is_module_workflow_compiled_pattern_wrong_text_model_workload' tests/benchmarks/benchmark_test_support.py"` currently fails only because the exact shared-support seam this task should remove is still present.

## Completion
- Moved the compiled-pattern wrong-text-model spec/source-workload/CPython probe/payload-round-trip/signature/selector family from `tests/benchmarks/benchmark_test_support.py` into `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Kept shared compiled-pattern success support in `tests/benchmarks/benchmark_test_support.py` under shared-only success signature helpers, and routed the remaining `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` wrong-text-model definition back through the source-tree owner module with lazy private wrappers instead of re-exporting the moved names.
- Updated the benchmark support ownership tests plus the manifest-validation and source-tree combined-suite tests to consume the wrong-text-model helpers from the source-tree owner module.
- Verification completed:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_wrong_text_model_selector_accepts_bounded_trio or run_cpython_compiled_pattern_module_helper_workload_materializes_finditer or module_workflow_compiled_pattern_correctness_case_signature_requires_compiled_module_call_shape'`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_specs|def _compiled_pattern_wrong_text_model_source_workloads|def _run_cpython_compiled_pattern_module_helper_workload|def _assert_wrong_text_model_payload_round_trip|def _module_workflow_compiled_pattern_correctness_case_signature|def _module_workflow_compiled_pattern_workload_signature|def _is_module_workflow_compiled_pattern_wrong_text_model_workload' tests/benchmarks/benchmark_test_support.py"`
