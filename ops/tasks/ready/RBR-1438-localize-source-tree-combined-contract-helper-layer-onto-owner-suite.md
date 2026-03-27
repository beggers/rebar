## RBR-1438: Localize source-tree-combined contract helper layer onto owner suite

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining source-tree-combined-only contract helper layer from `tests/benchmarks/benchmark_test_support.py` now that its live consumers are confined to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- The live reference scan in this run showed that `assert_benchmark_manifest_contract(...)`, `find_manifest_record(...)`, `run_correctness_case_with_cpython(...)`, and `manifest_workload_ids_matching(...)` are still defined in shared benchmark support even though no other benchmark suite imports them.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers while moving this last owner-only contract surface onto the source-tree-combined owner suite and teaching the benchmark-support meta-tests to validate that ownership directly.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move or inline the source-tree-combined-only contract helper layer out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so shared support no longer exports:
  - `assert_benchmark_manifest_contract(...)`
  - `find_manifest_record(...)`
  - `run_correctness_case_with_cpython(...)`
  - `manifest_workload_ids_matching(...)`
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to call those helpers locally instead of routing through `tests.benchmarks.benchmark_test_support`.
- Extend `tests/benchmarks/test_benchmark_test_support.py` so the meta-tests assert that this contract-helper surface now belongs to the source-tree-combined owner suite and no longer appears on shared benchmark support.
- Keep the run bounded to that ownership cleanup:
  - do not move `find_workload_record(...)`, `find_workload_document(...)`, or `assert_benchmark_workload_contract(...)`; shared support still uses those through `assert_manifest_workload_contracts(...)`
  - do not move manifest loading, workload execution, cache-clearing, or shared payload/result helpers that still have multi-suite consumers
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_combined_suite_owns or benchmark_test_support_owns'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_rows_keep_collection_replacement_manifest_measured'`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def (assert_benchmark_manifest_contract|find_manifest_record|run_correctness_case_with_cpython|manifest_workload_ids_matching)\\b' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - The state-file scan found no reserved unfiled `RBR-` ids above the filed frontier, so `RBR-1438` was available.
- Candidate selection in this run:
  - `python3` AST/reference scans across `tests/benchmarks/*.py` showed that `assert_benchmark_manifest_contract`, `find_manifest_record`, `run_correctness_case_with_cpython`, and `manifest_workload_ids_matching` each still have exactly one external benchmark consumer: `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - The same scan showed that `find_workload_record`, `find_workload_document`, and `assert_benchmark_workload_contract` are not part of this task because `tests/benchmarks/benchmark_test_support.py` still uses them internally via `assert_manifest_workload_contracts(...)`.
  - `bash -lc "! rg -n '^def (assert_benchmark_manifest_contract|find_manifest_record|run_correctness_case_with_cpython|manifest_workload_ids_matching)\\b' tests/benchmarks/benchmark_test_support.py"` is currently red because the source-tree-combined helper layer still lives in shared benchmark support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_combined_suite_owns or benchmark_test_support_owns'` passed with `11 passed, 191 deselected in 0.25s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_rows_keep_collection_replacement_manifest_measured'` passed with `1 passed, 306 deselected in 0.26s`.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
