# RBR-1327: Route source-tree compiled-pattern wrong-text-model contract surface through owner module

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete one more owner-specific shared-support dependency from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by routing the source-tree suite's compiled-pattern wrong-text-model contract bundle through `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must stop reaching the compiled-pattern wrong-text-model contract bundle through `benchmark_test_support.` for these names:
  - `_compiled_pattern_wrong_text_model_specs`
  - `_compiled_pattern_wrong_text_model_source_workloads`
  - `_compiled_pattern_wrong_text_model_contract_spec`
  - `compiled_pattern_contract_expected_build_calls`
  - `_compiled_pattern_module_helper_route`
- Route that bundle through the suite's existing `source_tree_support` module import instead of rebinding the names locally in the suite.
- Keep the ownership cleanup structural:
  - add the routed surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, alias shim, or wrapper layer
  - do not move the underlying contract-building logic out of `tests/benchmarks/benchmark_test_support.py`
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` with focused ownership checks that prove:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` exposes the routed compiled-pattern wrong-text-model contract surface
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer references those five names through `benchmark_test_support`
- Keep the cleanup structural only:
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_wrong_text_model'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_routes_moved_compiled_pattern_compile_contract_surfaces_through_source_tree_support'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in {'_compiled_pattern_wrong_text_model_specs','_compiled_pattern_wrong_text_model_source_workloads','_compiled_pattern_wrong_text_model_contract_spec','compiled_pattern_contract_expected_build_calls','_compiled_pattern_module_helper_route'}}); sys.exit(0 if not direct else 1)"`

## Constraints
- Keep the cleanup bounded to the compiled-pattern wrong-text-model contract bundle in the source-tree combined benchmark suite and the owner-surface tests that pin that routing.
- Prefer deleting direct shared-support lookups from the large suite over introducing another indirection layer.

## Notes
- `RBR-1327` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1327*' -o -name 'RBR-1328*' -o -name 'RBR-1329*' \) | sort` returned no matches before this task was queued
  - `rg -n 'RBR-1327|RBR-1328|RBR-1329' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical mentions inside completed task notes, not a live reservation for `RBR-1327`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime snapshot shows the most recent `architecture-implementation` run finishing `done`
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still references the compiled-pattern wrong-text-model contract bundle through `benchmark_test_support` at 8 call sites across these five names:
    - `_compiled_pattern_wrong_text_model_specs` (`2`)
    - `_compiled_pattern_wrong_text_model_source_workloads` (`2`)
    - `_compiled_pattern_wrong_text_model_contract_spec` (`2`)
    - `compiled_pattern_contract_expected_build_calls` (`1`)
    - `_compiled_pattern_module_helper_route` (`1`)
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_wrong_text_model'` passed with `6 passed, 273 deselected in 0.11s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_moved_combined_case_surface or combined_suite_routes_moved_compiled_pattern_compile_contract_surfaces_through_source_tree_support'` passed with `2 passed, 51 deselected in 0.14s`
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=sorted({node.attr for node in ast.walk(mod) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id=='benchmark_test_support' and node.attr in {'_compiled_pattern_wrong_text_model_specs','_compiled_pattern_wrong_text_model_source_workloads','_compiled_pattern_wrong_text_model_contract_spec','compiled_pattern_contract_expected_build_calls','_compiled_pattern_module_helper_route'}}); sys.exit(0 if not direct else 1)"` currently fails because the source-tree suite still reaches that wrong-text-model bundle through `benchmark_test_support`, and that failure belongs exactly to this cleanup
