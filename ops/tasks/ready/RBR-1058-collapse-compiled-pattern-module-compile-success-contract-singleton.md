# RBR-1058: Collapse the compiled-pattern `module.compile` success contract singleton

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining singleton-only success-contract plumbing in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the compiled-pattern `module.compile` success contract surface derives from the same owner-spec lane already used for the success anchors, instead of separate tuple reducers plus one free-floating contract-case constant.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines any of these singleton success-contract intermediates:
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_SOURCE_SELECTORS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_EXPECTED_ANCHOR_PAIRS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE`
- `_CompiledPatternModuleCompileSuccessOwnerSpec`, or a strictly smaller same-file replacement, owns the success-contract inputs now needed by both of these consumers:
  - the success anchor-definition expansion under `STANDARD_BENCHMARK_ANCHOR_CONTRACT_DEFINITIONS`;
  - the combined success entry inside `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`.
- Keep the current success contract shape intact after the refactor:
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` still contains exactly one combined success contract case followed by the keyword owner-spec contract cases;
  - the combined success case still keeps `case_id == "success"`;
  - the combined success case still keeps the same contract filenames:
    - `python_benchmark_compiled_pattern_module_compile_contract.py`
    - `python_benchmark_compiled_pattern_module_compile_anchor_contract.py`
  - the combined success case still keeps the same note text, excluded fields, payload-round-trip behavior, callback flag selection, and CPython dispatch path from `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE`.
- Keep the two bounded success slices intact while routing the contract inputs through the owner-spec surface:
  - `literal`
  - `named-group`
- Preserve the current per-slice semantics exactly after the cleanup:
  - both slices still route through `_module_workflow_compiled_pattern_compile_correctness_case_signature(...)`, `_module_workflow_compiled_pattern_compile_workload_signature(...)`, and `_is_module_workflow_compiled_pattern_compile_success_workload(...)`;
  - both slices still keep `expected_exception is None`, `kwargs == {}`, `use_compiled_pattern is True`, and `flags == 0`;
  - the literal slice still remains pinned to pattern `"abc"`;
  - the named-group slice still remains pinned to pattern `"(?P<word>abc)"`;
  - the two anchor-definition names stay unchanged:
    - `module-workflow-compiled-pattern-module-compile-literal-success`
    - `module-workflow-compiled-pattern-module-compile-named-group-success`

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_boundary_manifest_keeps_compiled_pattern_module_compile_keyword_rows_measured or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases or compiled_pattern_module_compile_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing'`
- `bash -lc "! rg -n '^_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_(SOURCE_SELECTORS|EXPECTED_ANCHOR_PAIRS|CONTRACT_CASE)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the singleton success-contract plumbing over introducing another support module, registry file, generated artifact, or checked-in data layer.
- Do not widen into the keyword owner specs, benchmark workload manifests under `benchmarks/workloads/`, harness code under `python/rebar_harness/`, implementation code, reports, or tracked project-state prose.

## Notes
- `RBR-1058` is the next available unreserved task id in the current checkout:
  - `RBR-1057` is the live ready feature task in `ops/tasks/ready/RBR-1057-publish-pattern-subn-bytes-single-match.md`; and
  - `rg -n 'RBR-1057|RBR-1058|RBR-1059|RBR-1060|RBR-1061' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked` returned matches only for `RBR-1057` in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 1`, `in_progress: 0`, and `blocked: 0`;
  - the newest dashboard shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path; and
  - the focused benchmark-contract pytest slice above already passes in the live checkout (`75 passed, 647 deselected, 18 subtests passed`).
- The remaining singleton cleanup target is concrete in the live checkout:
  - `_CompiledPatternModuleCompileSuccessOwnerSpec` still sits at line `7565`;
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_SOURCE_SELECTORS` and `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_EXPECTED_ANCHOR_PAIRS` still sit at lines `7664` and `7668`; and
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_CASE` still sits at line `17224`.
