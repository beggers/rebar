## RBR-1300: Move generic benchmark broker helpers onto benchmark_test_support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Stop using `tests/benchmarks/source_tree_benchmark_anchor_support.py` as the generic benchmark-helper broker by moving its remaining shared CPython execution, anchored-pair, and module-workflow-keyword support onto `tests/benchmarks/benchmark_test_support.py`, so the source-tree module is left owning only source-tree-specific manifest/expectation logic.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`

## Acceptance Criteria
- Move this generic helper surface off `tests/benchmarks/source_tree_benchmark_anchor_support.py` and onto `tests/benchmarks/benchmark_test_support.py` without changing behavior:
  - `AnchoredWorkloadCasePair`
  - `anchored_workload_case_ids`
  - `unanchored_workload_ids`
  - `expected_anchored_workload_case_pairs`
  - `assert_anchored_workload_case_result_parity`
  - `run_benchmark_workload_with_cpython`
  - `run_correctness_case_with_cpython`
  - `assert_benchmark_workload_matches_expected_result`
  - `_module_workflow_keyword_workload_args`
  - `_module_workflow_keyword_correctness_case_signature`
  - `_module_workflow_keyword_workload_signature`
  - `_is_module_workflow_keyword_flags_workload`
  - `_is_module_workflow_keyword_error_workload`
  - `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS`
- Keep `STANDARD_BENCHMARK_DEFINITIONS` built directly in `tests/benchmarks/benchmark_test_support.py` and splice the moved `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS` from that same module, preserving:
  - the existing owner-block order;
  - definition object identity for the moved module-workflow-keyword definitions; and
  - the current anchored/unanchored workload selection and manual-CPython parity behavior.
- Update the non-source-tree import sites so they consume the moved shared helpers from `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/source_tree_benchmark_anchor_support.py`. This includes:
  - `tests/benchmarks/benchmark_test_support.py`
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Move the ownership/contract assertions for the moved helper surface onto `tests/benchmarks/test_benchmark_test_support.py`. After this cleanup, `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` should only preserve source-tree-specific manifest/expectation helpers, not the moved generic broker surface.
- Remove the moved definitions from `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of leaving duplicate implementations, compatibility aliases, or forwarding re-exports behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `bash -lc "! rg -n -U -P \"from tests\\.benchmarks\\.source_tree_benchmark_anchor_support import \\([\\s\\S]*?(run_benchmark_workload_with_cpython|assert_benchmark_workload_matches_expected_result|_is_module_workflow_keyword_error_workload|_is_module_workflow_keyword_flags_workload|_module_workflow_keyword_correctness_case_signature|_module_workflow_keyword_workload_signature|MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS|anchored_workload_case_ids|unanchored_workload_ids|expected_anchored_workload_case_pairs)\" tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Do not add a new helper broker module or a compatibility wrapper. The point is to centralize genuinely shared support in `tests/benchmarks/benchmark_test_support.py` and delete duplication/brokering from the source-tree module.
- Preserve the source-tree-specific expectation and manifest-shape surface in `tests/benchmarks/source_tree_benchmark_anchor_support.py`; only the generic broker helpers should move.

## Notes
- `RBR-1300` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run;
  - `rg -n "RBR-1300|RBR-1301|RBR-1302|RBR-1303" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1300`; and
  - the newest live task before this file was `ops/tasks/done/RBR-1299-delete-standard-benchmark-anchor-wrapper-module.md`.
- No blocked architecture task existed to reopen or retire first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/dashboard.md` showed no inherited-dirty or refresh/commit anomaly in the latest cycle snapshot.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` is still `4918` lines and currently owns both source-tree-specific expectations and generic broker helpers;
  - `tests/benchmarks/benchmark_test_support.py` still imports `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS`, `anchored_workload_case_ids`, and `unanchored_workload_ids` from that source-tree module even though they are shared support; and
  - `rg -n -U -P "from tests\\.benchmarks\\.source_tree_benchmark_anchor_support import \\([\\s\\S]*?(run_benchmark_workload_with_cpython|assert_benchmark_workload_matches_expected_result|_is_module_workflow_keyword_error_workload|_is_module_workflow_keyword_flags_workload|_module_workflow_keyword_correctness_case_signature|_module_workflow_keyword_workload_signature|MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS|anchored_workload_case_ids|unanchored_workload_ids|expected_anchored_workload_case_pairs)" tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/benchmark_test_support.py"` currently reports live source-tree imports of the shared broker surface listed above.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed with `827 passed, 3 skipped, 3471 subtests passed in 42.41s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` passed with `830 tests collected in 0.19s`; and
  - the negative multiline `rg` command above currently fails because the shared broker surface still imports from `tests/benchmarks/source_tree_benchmark_anchor_support.py`, and that failure belongs exactly to this cleanup.
