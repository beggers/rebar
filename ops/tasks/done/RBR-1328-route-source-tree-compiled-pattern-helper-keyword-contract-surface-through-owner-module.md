# RBR-1328: Route source-tree compiled-pattern helper-keyword contract surface through owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete one more owner-specific shared-support dependency from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by routing the compiled-pattern helper-keyword contract bundle through `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must stop reaching the compiled-pattern helper-keyword contract bundle through `benchmark_test_support.` for these names:
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
  - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC`
  - `_is_collection_replacement_compiled_pattern_keyword_error_workload`
  - `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call`
- Route that bundle through the suite's existing `source_tree_support` module import instead of rebinding the names locally in the suite.
- Keep the ownership cleanup structural:
  - add the routed surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, alias shim, or wrapper layer
  - do not move the underlying contract-building logic out of `tests/benchmarks/benchmark_test_support.py`
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` with focused ownership checks that prove:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` exposes the routed helper-keyword contract surface
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer references those nine names through `benchmark_test_support`
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_routes_moved_support_surfaces_through_source_tree_support'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -c "import ast,pathlib,sys; names={'_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC','_is_collection_replacement_compiled_pattern_keyword_error_workload','_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call'}; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in names}); sys.exit(0 if not direct else 1)"`

## Constraints
- Keep the cleanup bounded to the compiled-pattern helper-keyword contract bundle in the source-tree combined benchmark suite and the owner-surface tests that pin that routing.
- Prefer deleting direct shared-support lookups from the large suite over introducing another indirection layer.

## Notes
- `RBR-1328` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f | sed 's#.*/##' | sort | tail -n 5` ended at `RBR-1327-...`
  - `rg -n 'RBR-1328|RBR-1329|RBR-1330' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside completed task notes, not a live reservation for `RBR-1328`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the current queue is empty, so this task seeds the next bounded architecture cleanup instead of colliding with inherited task churn
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still references the helper-keyword contract bundle through `benchmark_test_support` at 11 call sites across these nine names:
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS` (`2`)
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS` (`1`)
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC` (`2`)
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS` (`1`)
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS` (`1`)
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES` (`1`)
    - `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC` (`2`)
    - `_is_collection_replacement_compiled_pattern_keyword_error_workload` (`1`)
    - `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call` (`1`)
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'` passed with `66 passed, 213 deselected in 0.27s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_routes_moved_support_surfaces_through_source_tree_support'` passed with `5 passed, 51 deselected in 0.38s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `python3 -c "import ast,pathlib,sys; names={'_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC','_is_collection_replacement_compiled_pattern_keyword_error_workload','_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call'}; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in names}); sys.exit(0 if not direct else 1)"` currently fails because the source-tree suite still reaches that helper-keyword bundle through `benchmark_test_support`, and that failure belongs exactly to this cleanup

## Completion
- Routed the compiled-pattern helper-keyword contract bundle through `tests/benchmarks/source_tree_benchmark_anchor_support.py` and switched the combined source-tree benchmark suite to consume those nine names only through `source_tree_support`.
- Added owner-surface coverage proving the support module re-exports the helper-keyword bundle and the combined suite no longer reaches that bundle through `benchmark_test_support`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword'` -> `66 passed, 213 deselected`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_routes_moved_support_surfaces_through_source_tree_support'` -> `6 passed, 51 deselected`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `python3 -c "import ast,pathlib,sys; names={'_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_SOURCE_WORKLOADS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SOURCE_WORKLOAD_PARAMS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_PRECOMPILE_SOURCE_WORKLOAD_PARAMS','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES','_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC','_is_collection_replacement_compiled_pattern_keyword_error_workload','_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call'}; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in names}); sys.exit(0 if not direct else 1)"`
