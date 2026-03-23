# RBR-1070: Collapse source-tree contract anchor lanes

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the last two bespoke source-tree contract anchor tests in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so compiled-pattern contract anchor coverage flows through one shared file-local lane instead of two adjacent copy-shaped pytest bodies.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines either of these dedicated anchor tests:
  - `test_compiled_pattern_module_success_rows_stay_anchored_to_published_correctness_cases`
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases`
- Replace that split with one explicit same-file carrier plus one shared pytest body, or a strictly smaller equivalent:
  - keep the change file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - cover both `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS` and `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` through the same shared anchor-test path instead of leaving two parallel test functions behind; and
  - avoid introducing a new support module, registry file, generated artifact, or another detached helper family.
- Preserve the current contract-anchor semantics exactly after the cleanup:
  - `_COMPILED_PATTERN_MODULE_SUCCESS_ANCHOR_SPECS` still carries the same `contract_filename`, `correctness_case_signature`, `workload_signature`, `include_workload`, and `expected_anchored_pairs` values for the collection/replacement and module-boundary verbose-bytes slices;
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` still carries the same `anchor_contract_filename`, `correctness_case_signature`, `workload_signature`, `include_workload`, and `expected_anchor_pairs` values for the success and keyword cases; and
  - the shared anchor-test lane still checks anchored case ids, unanchored workload ids, and the exact anchored workload/case pairs for both families.
- Preserve the surrounding source-tree contract coverage exactly after the cleanup:
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation` still covers `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`;
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation` still covers `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads` still covers `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`;
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads` still covers `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`;
  - `test_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing` still covers `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`; and
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing` still covers `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`.
- Keep the cleanup structural only:
  - do not widen into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, correctness fixtures, implementation code, reports, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids'`
- `bash -lc "! rg -n '^def test_compiled_pattern_module_success_rows_stay_anchored_to_published_correctness_cases\\(|^def test_compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting parallel anchor-test plumbing over adding another id-keyed indirection layer.
- Preserve the current contract filenames, source workload selection, anchored workload ids, correctness case ids, and callback/probe semantics exactly.

## Notes
- `RBR-1070` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty before this file is added; and
  - `rg -n 'RBR-1070|RBR-1071|RBR-1072' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned only historical notes inside done-task files, not a live reservation or task file for those ids.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The redundancy is concrete in the live checkout:
  - `test_compiled_pattern_module_success_rows_stay_anchored_to_published_correctness_cases` still sits at line `16798`;
  - `test_compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases` still sits at line `17419`; and
  - both functions still perform the same anchored-case / unanchored-workload / expected-pair assertion shape against source-tree contract manifests built from adjacent spec carriers.
- The focused verification slice is already green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_rows_until_helper_invocation or standard_benchmark_manifest_preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or run_internal_workload_probe_measures_compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_workloads or run_internal_workload_probe_measures_compiled_pattern_module_compile_success_and_keyword_contract_workloads or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_compile_success_and_keyword_contract_callbacks_precompile_first_argument_before_timing or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids'` returned `173 passed, 549 deselected` in this run.
- The structural grep still shows the exact duplication this task is meant to remove:
  - `rg -n '^def test_compiled_pattern_module_success_rows_stay_anchored_to_published_correctness_cases\\(|^def test_compiled_pattern_module_compile_success_and_keyword_contract_rows_stay_anchored_to_published_correctness_cases\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned both function definitions in this run.
