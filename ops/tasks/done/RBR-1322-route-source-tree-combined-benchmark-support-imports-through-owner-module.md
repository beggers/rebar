Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Completion
- Completed on 2026-03-25.
- Removed the direct `from tests.benchmarks.benchmark_test_support import ...` wall from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and routed the combined suite through the existing `from tests.benchmarks import benchmark_test_support` owner-module import.
- Updated `tests/benchmarks/test_benchmark_test_support.py` to assert the combined suite now imports `benchmark_test_support` only through `tests.benchmarks`, carries no direct owner `ImportFrom` edge, does not alias the retired owner surface locally, and no longer exposes the retired owner names in its top-level definition/assignment namespace.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'runner_regenerates_source_tree_scorecards or compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'`, `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces'`, `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'shared_module_boundary_manifest_path_consumers_reuse_support_constant_by_identity or shared_collection_replacement_classifier_contract_tests_import_from_support or shared_compiled_pattern_helper_contract_tests_import_from_support or compiled_pattern_module_compile_surviving_suites_import_shared_support_exports or source_tree_combined_suite_imports_standard_benchmark_definitions_from_support'`, and the task AST probe command.

## Goal
- Delete the remaining 60-name direct `benchmark_test_support` owner import wall from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark suite reaches that shared support surface only through its existing `from tests.benchmarks import benchmark_test_support` owner-module import.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must stop using `from tests.benchmarks.benchmark_test_support import ...`.
- The combined benchmark suite must route the current direct owner surface through the existing `benchmark_test_support` module import instead of binding owner-owned names locally. This includes the current direct wall that covers:
  - standard benchmark definitions and manifest-path constants
  - compiled-pattern compile-contract cases, owner specs, and anchor lanes
  - source-tree contract builders, manifest/workload helpers, and manifest-writing helpers
  - shared benchmark assertion/report helpers and workload selectors
  - module-workflow, pattern-boundary, and compile-proxy signature helpers and workload classifiers
- Update `tests/benchmarks/test_benchmark_test_support.py` with one focused AST/import ownership check that proves:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer has a direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support`
  - the suite still imports `benchmark_test_support` through `tests.benchmarks`
  - the owner-owned names retired by this cleanup are absent from the combined suite's top-level definition/assignment namespace
- Do not add a new helper module, alias shim, wrapper, or re-export layer. Reuse the existing `tests.benchmarks import benchmark_test_support` owner-module import already present in the suite.
- Keep the cleanup structural:
  - do not move support logic out of `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'runner_regenerates_source_tree_scorecards or compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces'`
- `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.benchmark_test_support']; aliases=[(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names if a.name=='benchmark_test_support' and a.asname is None]; sys.exit(0 if (not direct and aliases) else 1)"`

## Constraints
- Keep the cleanup bounded to import ownership in the combined benchmark suite plus the supporting AST/import contract test.
- Prefer deleting direct owner-name bindings over introducing another indirection layer.

## Notes
- `RBR-1322` is the next available unreserved task id in this checkout:
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1322*' -o -name 'RBR-1323*' -o -name 'RBR-1324*' \) | sort` returned no matches before this task was queued; and
  - `rg -n "RBR-1322|RBR-1323|RBR-1324" ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` matched only historical notes inside already-completed task files, not a live reservation for `RBR-1322`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready `feature-implementation` work, no blocked tasks, and the most recent `architecture-implementation` run finishing `done`
  - the latest runtime dashboard reports no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still contains one direct `ImportFrom` edge to `tests.benchmarks.benchmark_test_support`
  - a current AST probe in this run reported `60` directly imported owner names on that edge
  - the same suite already imports `benchmark_test_support` through `tests.benchmarks`, so the direct owner import wall is now shadow owner plumbing rather than a required access path
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'runner_regenerates_source_tree_scorecards or compiled_pattern_module_success_callbacks_precompile_first_argument_before_timing'` passed with `14 passed, 265 deselected, 430 subtests passed in 1.83s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_consumer_suites_reuse_shared_support_without_local_duplicates or compiled_pattern_contract_consumer_suites_do_not_alias_owner_module_surfaces'` passed with `3 passed, 112 deselected in 0.17s`
  - `python3 -c "import ast,pathlib,sys; mod=ast.parse(pathlib.Path('tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py').read_text()); direct=[n for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks.benchmark_test_support']; aliases=[(a.name,a.asname) for n in mod.body if isinstance(n, ast.ImportFrom) and n.module=='tests.benchmarks' for a in n.names if a.name=='benchmark_test_support' and a.asname is None]; sys.exit(0 if (not direct and aliases) else 1)"` currently fails because the combined suite still carries the direct owner import wall, and that failure belongs exactly to this cleanup
