# RBR-1068: Retire pattern wrong-text-model anchor singleton

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining one-off pattern-helper collection/replacement wrong-text-model anchor test in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so that anchor coverage for that slice flows only through the existing `StandardBenchmarkAnchorContractDefinition` lane and the shared generic anchor assertions instead of a duplicate bespoke test body.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer defines `test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases`.
- Keep the tracked anchor contract for the same slice on the existing standard-definition lane rather than replacing the singleton with another custom helper or another dedicated parametrized family:
  - `STANDARD_BENCHMARK_DEFINITIONS` still contains the `StandardBenchmarkAnchorContractDefinition` named `pattern-helper-collection-replacement-wrong-text-model`;
  - that definition still targets only `COLLECTION_REPLACEMENT_MANIFEST_PATH`;
  - its expected anchor mapping still stays exactly:
    - `pattern-split-on-bytes-string-warm-str` -> `workflow-pattern-split-str-pattern-on-bytes-string`
    - `pattern-sub-on-bytes-string-warm-str` -> `workflow-pattern-sub-str-pattern-on-bytes-string`
    - `pattern-subn-on-str-string-purged-bytes` -> `workflow-pattern-subn-bytes-pattern-on-str-string`
  - its signature helpers still stay `_collection_replacement_pattern_wrong_text_model_correctness_case_signature`, `_collection_replacement_pattern_wrong_text_model_workload_signature`, and `_is_collection_replacement_pattern_wrong_text_model_workload`.
- Preserve the shared wrong-text-model owner-spec lane exactly after the cleanup:
  - `WRONG_TEXT_MODEL_OWNER_SPECS` still contains `_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_OWNER_SPEC`;
  - `test_standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation` still covers that owner spec;
  - `test_run_internal_workload_probe_measures_wrong_text_model_contract_workloads` still covers that owner spec; and
  - `test_wrong_text_model_callbacks_preserve_precompile_contract` still covers that owner spec.
- Keep the change structural only:
  - do not widen into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, support helpers, implementation code, reports, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'`
- `bash -lc "! rg -n '^def test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the change limited to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Prefer deleting the redundant singleton over introducing another anchor-spec helper, registry entry, or support module.
- Preserve the existing anchor mapping, manifest path, signature helpers, and wrong-text-model owner-spec semantics exactly.

## Notes
- `RBR-1068` is the next available unreserved architecture-task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty; and
  - `rg -n 'RBR-1068|RBR-1069|RBR-1070|RBR-1071' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned only a historical note inside `ops/tasks/done/RBR-1066-collapse-compiled-pattern-module-success-anchor-singletons.md`, not a live reservation or task file for those ids.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-ready-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The redundancy is concrete in the live checkout:
  - `STANDARD_BENCHMARK_DEFINITIONS` already includes the `pattern-helper-collection-replacement-wrong-text-model` anchor definition at line `9864`;
  - the generic tests `test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases` and `test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids` already cover that definition; and
  - the remaining bespoke singleton `test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases` still sits at line `15122`.
- The focused verification slice already passes in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'` returned `47 passed, 676 deselected` in this run.

## Completion Note
- Removed the one-off `test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases` singleton from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and left the existing `StandardBenchmarkAnchorContractDefinition` plus wrong-text-model owner-spec coverage untouched.
- Preserved the existing `pattern-helper-collection-replacement-wrong-text-model` definition, its manifest path, its anchor mapping, and its signature helpers exactly as-is.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_manifest_preserves_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_wrong_text_model_contract_workloads or wrong_text_model_callbacks_preserve_precompile_contract'` -> `123 passed, 599 deselected`
  - `bash -lc "! rg -n '^def test_pattern_helper_collection_replacement_wrong_text_model_rows_stay_anchored_to_published_correctness_cases\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> success
