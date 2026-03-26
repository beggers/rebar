## RBR-1359: Move wrong-text-model contract specs onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned transit layer for non-source-tree wrong-text-model benchmark contract specs so shared contract metadata lives on `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Move these contract-spec constants into `tests/benchmarks/benchmark_test_support.py`:
  - `_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume the shared contract specs and delete the local definitions entirely.
- Update the touched benchmark suites to call the shared contract specs from `tests.benchmarks.benchmark_test_support` directly instead of routing them through `source_tree_support`.
- Update the source-tree owner-surface inventories/tests so those contract-spec names are no longer treated as source-tree-owned or source-tree-routed support.
- Keep the cleanup bounded to contract-spec relocation:
  - do not change workload selectors, manifest payload semantics, or runtime benchmark behavior
  - do not move source-tree-specific wrong-text-model selectors or source-workload discovery out of `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a replacement wrapper, alias shim, or new helper module

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'test_standard_benchmark_manifest_preserves_pattern_boundary_wrong_text_model_rows_until_helper_invocation or test_run_internal_workload_probe_measures_pattern_boundary_wrong_text_model_contract_workloads or test_pattern_boundary_wrong_text_model_callbacks_preserve_precompile_contract'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `rg -n '^(_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC)\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^(_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC)\\b' tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py"`

## Constraints
- Prefer deleting the source-tree transit layer over moving it sideways; these contract specs shape shared benchmark contract rows rather than source-tree-owned combined-slice expectations.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree-specific selectors, expectations, and owner inventories after the cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1359|RBR-1360|RBR-1361|RBR-1362' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned only historical mentions inside completed task notes, so no higher frontier ID in that range was reserved
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still locally defines `_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS` and `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC` even though both constants describe shared contract-row shaping for collection-replacement, module-boundary, and pattern-boundary wrong-text-model workloads rather than source-tree combined-owner logic
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_benchmark_manifest_validation.py` still reach those shared contract specs through `source_tree_support`
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still treats `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC` and `_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS` as part of the source-tree owner surface, so deleting the transit layer requires one bounded cross-file reroute rather than a grep-only cleanup
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'test_standard_benchmark_manifest_preserves_pattern_boundary_wrong_text_model_rows_until_helper_invocation or test_run_internal_workload_probe_measures_pattern_boundary_wrong_text_model_contract_workloads or test_pattern_boundary_wrong_text_model_callbacks_preserve_precompile_contract'` passed with `10 passed, 17 deselected in 0.18s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or test_compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'` passed with `6 passed, 273 deselected in 0.20s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'` passed with `5 passed, 59 deselected in 0.11s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `rg -n '^(_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC)\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared benchmark support module does not yet define those contract specs, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^(_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because both contract-spec definitions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(_COMPILED_PATTERN_WRONG_TEXT_MODEL_CONTRACT_SPECS|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC)\\b' tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py"` currently fails because those suites still route the shared contract specs through `source_tree_support`, and that failure belongs exactly to this cleanup
