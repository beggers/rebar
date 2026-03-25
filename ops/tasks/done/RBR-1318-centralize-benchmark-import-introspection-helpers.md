# RBR-1318: Centralize benchmark import-introspection helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the remaining duplicated benchmark import-introspection layer so `tests/benchmarks/benchmark_test_support.py` owns the shared AST/import walkers and the benchmark contract suites stop carrying their own local copies.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Add canonical shared import-introspection helpers to `tests/benchmarks/benchmark_test_support.py` for the benchmark suites that currently duplicate this logic locally:
  - `_module_imported_names(...)`
  - `_module_import_targets(...)`
  - `_ast_import_targets(...)`
- Update `tests/benchmarks/test_benchmark_test_support.py` to reuse those shared helpers instead of defining its own local copies.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to reuse the same shared helper surface instead of defining its own local `_module_imported_names(...)`.
- Keep the ownership contract explicit in the benchmark tests:
  - adjust the affected AST/import assertions so they still prove the consumer suites read import metadata through the shared support owner
  - add or update one focused regression check that fails if these helper definitions reappear locally in either benchmark suite
- Do not add a new helper module, alias shim, or wrapper layer. Reuse the existing owner module `tests/benchmarks/benchmark_test_support.py`.
- Keep this cleanup structural:
  - do not move non-import-inspection benchmark logic out of the current owner modules
  - do not change benchmark workload manifests, runtime harness behavior, scorecard contents, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def (_module_imported_names|_module_import_targets|_ast_import_targets)\\(' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`
- `bash -lc \"[ \\\"$(rg -n '^def (_module_imported_names|_module_import_targets|_ast_import_targets)\\\\(' tests/benchmarks/benchmark_test_support.py | wc -l)\\\" -eq 3 ]\"`

## Constraints
- Keep the cleanup bounded to shared AST/import-introspection ownership in the benchmark contract layer.
- Prefer deleting the duplicated local helper definitions over introducing another indirection surface.

## Notes
- `RBR-1318` is the next available unreserved task id in this checkout:
  - `rg -n 'RBR-1318|RBR-1319|RBR-1320' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f \( -name 'RBR-1318*' -o -name 'RBR-1319*' -o -name 'RBR-1320*' \) | sort` returned no matches before this task was queued.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and no ready `feature-implementation` work
  - the latest runtime dashboard shows the most recent `architecture-implementation` run finishing `done` and no inherited-dirty, refresh, or commit anomaly
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_benchmark_test_support.py` still defines `_module_imported_names(...)`, `_module_import_targets(...)`, and `_ast_import_targets(...)` locally even though `tests/benchmarks/benchmark_test_support.py` already owns the shared `_parsed_module_ast(...)` surface they depend on
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still defines its own local `_module_imported_names(...)` with the same AST walk pattern
  - `rg -n '^def _module_imported_names\\(|^def _module_import_targets\\(|^def _ast_import_targets\\(' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/benchmark_test_support.py` currently reports four local helper definitions across the two consumer suites and none on the shared owner module
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `161 passed in 0.47s`
  - `bash -lc "! rg -n '^def (_module_imported_names|_module_import_targets|_ast_import_targets)\\(' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because both benchmark suites still define those helpers locally, and that failure belongs exactly to this cleanup
  - `bash -lc \"[ \\\"$(rg -n '^def (_module_imported_names|_module_import_targets|_ast_import_targets)\\\\(' tests/benchmarks/benchmark_test_support.py | wc -l)\\\" -eq 3 ]\"` currently fails because the shared owner module does not yet define those canonical helpers
- 2026-03-25T16:51:53+00:00: landed by moving `_module_imported_names(...)`, `_module_import_targets(...)`, and `_ast_import_targets(...)` into `tests/benchmarks/benchmark_test_support.py`, deleting the duplicated local definitions from `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, and adding a focused ownership regression in `tests/benchmarks/test_benchmark_test_support.py` that requires both consumer suites to import these helpers from the shared support owner instead of redefining them locally.
- Verification:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` -> `163 passed in 0.66s`
  - `bash -lc "! rg -n '^def (_module_imported_names|_module_import_targets|_ast_import_targets)\\(' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` -> passed
  - `bash -lc '[ "$(rg -n '^\"'\"'^def (_module_imported_names|_module_import_targets|_ast_import_targets)\\('\"'\"' tests/benchmarks/benchmark_test_support.py | wc -l)" -eq 3 ]'` -> passed
