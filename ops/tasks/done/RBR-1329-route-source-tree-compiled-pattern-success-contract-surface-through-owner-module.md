## RBR-1329: Route source-tree compiled-pattern success contract surface through owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete one more owner-specific shared-support dependency from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by routing the compiled-pattern success contract surface through `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must stop reaching the compiled-pattern success contract surface through `benchmark_test_support.` for these names:
  - `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`
  - `_assert_compiled_pattern_module_success_payload_round_trip`
- Route that surface through the suite's existing `source_tree_support` module import instead of rebinding the names locally in the suite.
- Keep the ownership cleanup structural:
  - add the routed surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, alias shim, or wrapper layer
  - do not move the underlying contract-building logic out of `tests/benchmarks/benchmark_test_support.py`
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` with focused ownership checks that prove:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` exposes the routed compiled-pattern success contract surface
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer references those two names through `benchmark_test_support`
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success_contract_workloads or compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -c "import ast,pathlib,sys; names={'_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS','_assert_compiled_pattern_module_success_payload_round_trip'}; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in names}); sys.exit(0 if not direct else 1)"`

## Constraints
- Keep the cleanup bounded to the compiled-pattern success contract surface in the source-tree combined benchmark suite and the owner-surface tests that pin that routing.
- Prefer deleting direct shared-support lookups from the large suite over introducing another indirection layer.

## Notes
- `RBR-1329` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f | sed 's#.*/##' | sort | tail -n 10` ended at `RBR-1328-...`
  - `rg -n 'RBR-1329|RBR-1330|RBR-1331' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside completed task notes, not a live reservation for `RBR-1329`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the current queue is empty, so this task seeds the next bounded architecture cleanup instead of colliding with inherited task churn
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still references `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS` and `_assert_compiled_pattern_module_success_payload_round_trip` through `benchmark_test_support`
  - `rg -n "_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS|_assert_compiled_pattern_module_success_payload_round_trip" tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently matches only the combined suite call sites, not owner-module exports or owner-surface tests
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success_contract_workloads or compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'` passed with `39 passed, 240 deselected in 0.12s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `60 passed in 0.95s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `python3 -c "import ast,pathlib,sys; names={'_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS','_assert_compiled_pattern_module_success_payload_round_trip'}; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in names}); print(direct); sys.exit(0 if not direct else 1)"` currently fails because the combined suite still reaches that compiled-pattern success contract surface through `benchmark_test_support`, and that failure belongs exactly to this cleanup

## Completion
- Routed `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS` and `_assert_compiled_pattern_module_success_payload_round_trip` through `tests/benchmarks/source_tree_benchmark_anchor_support.py`, repointed the combined suite to `source_tree_support`, and extended the owner-surface test to pin both routed names.
- Verification after the refactor:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success_contract_workloads or compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'` passed with `39 passed, 240 deselected in 0.19s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `60 passed in 1.05s`
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed
  - `python3 -c "import ast,pathlib,sys; names={'_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS','_assert_compiled_pattern_module_success_payload_round_trip'}; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in names}); print(direct); sys.exit(0 if not direct else 1)"` passed and printed `[]`
