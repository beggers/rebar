## RBR-1435: Localize benchmark-support AST owner-introspection layer onto meta-tests

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining AST/owner-introspection helper layer from `tests/benchmarks/benchmark_test_support.py` now that it no longer has any non-meta-test consumers.
- The live post-JSON probe in this run showed that the helper family below is only referenced by `tests/benchmarks/test_benchmark_test_support.py`, so shared benchmark support is still carrying a whole support-meta-only inspection layer.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers and move the support-self-inspection plumbing back onto the meta-test file that is the sole remaining consumer.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move or inline the support-meta-only AST/owner-surface inspection layer out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/test_benchmark_test_support.py` so shared support no longer exports these helpers:
  - `_parsed_module_ast(...)`
  - `_module_imported_names(...)`
  - `_module_import_targets(...)`
  - `_module_function_definition(...)`
  - `_module_assignment(...)`
  - `_module_class_definition(...)`
  - `_class_method_definition(...)`
  - `_ast_import_targets(...)`
  - `_module_alias_names(...)`
  - `_top_level_import_from_alias_pairs(...)`
  - `_module_attribute_alias_targets(...)`
  - `_owner_definition_manifest_path_names(...)`
  - `top_level_module_definition_and_assignment_names(...)`
  - `assert_owner_surface_module_owned_without_local_duplicates(...)`
  - `assert_mixed_owner_surface(...)`
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` to own that layer locally instead of routing those assertions through `tests.benchmarks.benchmark_test_support`.
- Keep the run bounded to that ownership cleanup:
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files
  - do not move helpers that still have real cross-suite consumers such as workload loading, CPython workload execution, result-parity assertions, or manifest/workload contract helpers outside this exact layer

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'module_imported_names or module_import_targets or ast_import_targets or module_assignment or class_method_definition or module_alias_names or module_attribute_alias_targets or mixed_owner_surface or owner_surface_module_owned_without_local_duplicates or top_level_module_definition_and_assignment_names'`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n '^def (_parsed_module_ast|_module_imported_names|_module_import_targets|_module_function_definition|_module_assignment|_module_class_definition|_class_method_definition|_ast_import_targets|_module_alias_names|_top_level_import_from_alias_pairs|_module_attribute_alias_targets|_owner_definition_manifest_path_names|top_level_module_definition_and_assignment_names|assert_owner_surface_module_owned_without_local_duplicates|assert_mixed_owner_surface)\\b' tests/benchmarks/benchmark_test_support.py"`

## Completion
- Moved the AST/owner-introspection helper layer out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/test_benchmark_test_support.py`, including local cache-reset plumbing for the meta-test-owned cached AST helpers.
- Verified the targeted benchmark meta-test slice passes (`28 passed, 172 deselected`), both files compile with `py_compile`, and the shared support module no longer defines any of the removed helper exports.

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1435*' -o -name 'RBR-1436*' -o -name 'RBR-1437*' \) | sort` returned no matches.
  - `rg -n "RBR-1435|RBR-1436|RBR-1437" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1435` was available.
- Candidate selection in this run:
  - First probe rejected: moving `assert_benchmark_manifest_contract(...)` and `find_manifest_record(...)` back out of shared support would fight the later centralization recorded in `ops/tasks/done/RBR-1358-centralize-benchmark-report-contract-helpers-onto-shared-support.md`, so that cleanup is not viable in the current checkout.
  - Second probe was viable: the AST/owner-introspection layer listed above still lives in `tests/benchmarks/benchmark_test_support.py`, and the live reference scan in this run showed those names only under `tests/benchmarks/test_benchmark_test_support.py`.
  - `bash -lc "! rg -n '^def (_parsed_module_ast|_module_imported_names|_module_import_targets|_module_function_definition|_module_assignment|_module_class_definition|_class_method_definition|_ast_import_targets|_module_alias_names|_top_level_import_from_alias_pairs|_module_attribute_alias_targets|_owner_definition_manifest_path_names|top_level_module_definition_and_assignment_names|assert_owner_surface_module_owned_without_local_duplicates|assert_mixed_owner_surface)\\b' tests/benchmarks/benchmark_test_support.py"` is currently red because that meta-test-only layer still lives in shared support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'module_imported_names or module_import_targets or ast_import_targets or module_assignment or class_method_definition or module_alias_names or module_attribute_alias_targets or mixed_owner_surface or owner_surface_module_owned_without_local_duplicates or top_level_module_definition_and_assignment_names'` passed with `28 passed, 172 deselected in 0.25s`.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py` passed.
