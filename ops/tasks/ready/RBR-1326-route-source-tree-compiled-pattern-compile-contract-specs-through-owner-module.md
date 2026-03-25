# RBR-1326: Route source-tree compiled-pattern compile contract specs through owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete one more broad shared-support dependency from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by routing the source-tree suite's compiled-pattern module-compile contract spec bundle through `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must stop reaching the compiled-pattern module-compile contract bundle through `benchmark_test_support.` for these names:
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES`
  - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS`
- Route that bundle through the suite's existing `source_tree_support` module import instead of rebinding the names locally in the suite.
- Keep the ownership cleanup structural:
  - add the routed surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, alias shim, or wrapper layer
  - do not move the underlying contract-building logic out of `tests/benchmarks/benchmark_test_support.py`
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` with focused ownership checks that prove:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` exposes the routed compiled-pattern compile contract surface
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer binds or references those five names through `benchmark_test_support`
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_no_longer_defines_moved_source_tree_case_surface_locally or combined_suite_no_longer_binds_centralized_source_tree_manifest_paths_locally'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in {'_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES','_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES','_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS','_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS','_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS'}}); sys.exit(0 if not direct else 1)"`

## Constraints
- Keep the cleanup bounded to the compiled-pattern module-compile contract bundle in the source-tree combined benchmark suite and the owner-surface tests that pin that routing.
- Prefer deleting direct shared-support lookups from the large suite over introducing another layer of indirection.

## Notes
- `RBR-1326` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1326|RBR-1327|RBR-1328' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside completed task notes, not a live reservation for `RBR-1326`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime snapshot shows the most recent `architecture-implementation` run finishing `done`
  - the only last-cycle anomaly is a `feature-planning` timeout, not inherited-dirty checkpoint churn or a post-task refresh/commit stall
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still references the compiled-pattern module-compile contract bundle through `benchmark_test_support` at `10` call sites across these five names:
    - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES` (`3`)
    - `_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES` (`2`)
    - `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS` (`1`)
    - `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS` (`2`)
    - `_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS` (`2`)
  - the current owner modules do not expose that bundle yet, so the large source-tree suite still reaches into shared support directly for owner-specific compile-contract metadata
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile'` passed with `77 passed, 202 deselected in 1.61s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_no_longer_defines_moved_source_tree_case_surface_locally or combined_suite_no_longer_binds_centralized_source_tree_manifest_paths_locally'` passed with `3 passed, 49 deselected in 0.13s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in {'_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES','_COMPILED_PATTERN_MODULE_CONTRACT_ANCHOR_LANES','_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_OWNER_SPECS','_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_OWNER_SPECS','_COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_SOURCE_WORKLOAD_PARAMS'}}); sys.exit(0 if not direct else 1)"` currently fails because the source-tree suite still reaches that compile-contract bundle through `benchmark_test_support`, and that failure belongs exactly to this cleanup
