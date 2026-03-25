# RBR-1314: Centralize shared benchmark AST introspection helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining duplicated AST/introspection helpers from the benchmark-support contract suites so those tests reuse one shared owner on `tests/benchmarks/benchmark_test_support.py` instead of parsing benchmark modules through parallel local helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Add shared benchmark-test-support helpers for the duplicated AST/introspection work that is currently reimplemented in both benchmark contract suites:
  - a helper that parses a module object into an `ast.Module`
  - a helper that extracts the tupled `manifest_paths` name references from an owner-definition assignment or builder return value
- Update `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to import and reuse those shared helpers instead of defining their own `_parsed_module_ast(...)` and `_owner_definition_manifest_path_names(...)` functions locally.
- Keep suite-specific AST helpers local when they are still genuinely suite-specific:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py::_parsed_source_tree_combined_suite_ast` should stay local
  - do not move deletion-only assertions like `_assert_deleted_benchmark_module_stays_absent(...)` unless they can directly reuse the new shared parser helper without adding another wrapper
- Do not add a new helper module, alias layer, or compatibility wrapper. Reuse the existing owner module `tests/benchmarks/benchmark_test_support.py`.
- Preserve the current benchmark-support contract coverage and ownership boundaries:
  - keep the deleted-wrapper/import-absence assertions in `tests/benchmarks/test_benchmark_test_support.py` passing
  - keep the owner manifest-path equality and owner-definition export assertions in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passing

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_from_support or deleted_pattern_boundary_support_stays_unimportable_and_unreferenced or benchmark_test_support_owns_compiled_pattern_module_success_surface'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'owner_manifest_path_constants_point_to_current_workload_files or owner_builders_reference_owner_manifest_path_constants or owner_definition_exports_reuse_owner_manifest_path_constants'`
- `bash -lc "! rg -n '^def (_parsed_module_ast|_owner_definition_manifest_path_names)\\(' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Keep this cleanup structural and bounded to shared benchmark test-support ownership. Do not change benchmark manifests, runtime harness behavior, published scorecards, README text, or tracked `ops/state/` prose.
- Prefer deleting duplicated suite-local helpers over broadening the support surface beyond the two reused AST/introspection helpers above.

## Notes
- `RBR-1314` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1314|RBR-1315|RBR-1316" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \\( -name 'RBR-1314*' -o -name 'RBR-1315*' -o -name 'RBR-1316*' \\) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`
  - the latest runtime dashboard showed no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_benchmark_test_support.py` still defines local `_parsed_module_ast(...)` and `_owner_definition_manifest_path_names(...)` helpers even though `tests/benchmarks/benchmark_test_support.py` already owns adjacent benchmark-module introspection via `top_level_module_definition_and_assignment_names(...)`
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` defines the same two helpers locally for the same benchmark-owner inspection boundary
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_from_support or deleted_pattern_boundary_support_stays_unimportable_and_unreferenced or benchmark_test_support_owns_compiled_pattern_module_success_surface'` passed with `5 passed, 88 deselected in 0.23s`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'owner_manifest_path_constants_point_to_current_workload_files or owner_builders_reference_owner_manifest_path_constants or owner_definition_exports_reuse_owner_manifest_path_constants'` passed with `3 passed, 45 deselected in 0.11s`
  - `bash -lc "! rg -n '^def (_parsed_module_ast|_owner_definition_manifest_path_names)\\(' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because both files still carry those duplicated helper definitions, and that failure belongs exactly to this cleanup.
