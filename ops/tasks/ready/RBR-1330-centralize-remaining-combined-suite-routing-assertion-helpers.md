## RBR-1330: Centralize remaining combined-suite routing assertion helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining duplicated AST/alias routing assertion layer from the benchmark contract suites so `tests/benchmarks/benchmark_test_support.py` owns the shared combined-suite routing helpers and the consumer suites stop carrying local walkers for the same ownership contract.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Add canonical shared helpers to `tests/benchmarks/benchmark_test_support.py` for the remaining combined-suite routing assertions that are still implemented locally in consumer suites:
  - parsing or loading the combined benchmark suite through the existing shared module-inspection surface
  - resolving imported module alias names across simple assignment alias chains
  - asserting that routed owner names stay behind the expected package-module alias instead of direct imports, local rebindings, or direct `benchmark_test_support` attribute access
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to reuse that shared owner-module surface instead of defining these local helpers:
  - `_parsed_source_tree_combined_suite_ast(...)`
  - `_module_alias_names(...)`
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` to reuse the same shared owner-module surface instead of defining its local `_assert_source_tree_combined_routes_owner_names_through_module_alias(...)` helper.
- Keep the ownership contract explicit in the benchmark tests:
  - adjust the affected routing assertions so they still prove `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reaches owner surfaces only through the intended package-module aliases
  - add or update one focused regression check in `tests/benchmarks/test_benchmark_test_support.py` that fails if those consumer-local helper definitions reappear
- Do not add a new helper module, alias shim, or wrapper layer. Reuse the existing owner module `tests/benchmarks/benchmark_test_support.py`.
- Keep this cleanup structural:
  - do not move benchmark workload-selection or contract-building logic out of its current owner modules
  - do not change benchmark manifests, harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def (_parsed_source_tree_combined_suite_ast|_module_alias_names|_assert_source_tree_combined_routes_owner_names_through_module_alias)\\(' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Constraints
- Keep the cleanup bounded to the remaining shared routing-assertion helpers for the source-tree combined benchmark suite and the tests that pin that ownership.
- Prefer deleting duplicated consumer-local walkers over adding another indirection surface.

## Notes
- `RBR-1330` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1330|RBR-1331|RBR-1332" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1330*' -o -name 'RBR-1331*' -o -name 'RBR-1332*' \) | sort` returned no matches before this task was queued
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime state shows the most recent `architecture-implementation` run finishing `done` with no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still defines `_parsed_source_tree_combined_suite_ast(...)` and `_module_alias_names(...)` locally
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still defines `_assert_source_tree_combined_routes_owner_names_through_module_alias(...)` locally
  - both suites are asserting routing for `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, while `tests/benchmarks/benchmark_test_support.py` already owns the broader shared AST/import-inspection surface they should build on
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `327 passed in 2.68s`
  - `bash -lc "! rg -n '^def (_parsed_source_tree_combined_suite_ast|_module_alias_names|_assert_source_tree_combined_routes_owner_names_through_module_alias)\\(' tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails because those consumer-local helpers still exist, and that failure belongs exactly to this cleanup
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
