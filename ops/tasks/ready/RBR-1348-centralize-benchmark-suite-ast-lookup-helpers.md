## RBR-1348: Centralize benchmark-suite AST lookup helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the duplicated generic AST lookup helpers from `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` by moving that shared lookup surface onto `tests/benchmarks/benchmark_test_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Add one shared AST lookup surface to `tests/benchmarks/benchmark_test_support.py` for the generic helper shapes that both suites currently hand-roll:
  - top-level function-definition lookup
  - top-level assignment lookup
  - top-level class-definition lookup
  - class-method-definition lookup
- Update `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to use that shared lookup surface instead of defining their own local `_module_assignment(...)` and `_module_function_definition(...)` helpers.
- Fold the single-suite-only generic helpers into the same shared surface when they fit naturally:
  - `tests/benchmarks/test_benchmark_test_support.py` should stop defining local `_module_class_definition(...)` and `_class_method_definition(...)` once the shared helper exists
  - keep `_top_level_package_import_alias_pairs(...)` and `_assert_owner_module_routes_through_package_import(...)` local unless the implementation can remove them without adding another wrapper layer
- Keep the cleanup structural only:
  - do not change benchmark manifests, benchmark harness behavior, scorecards, README text, or tracked `ops/state/` prose
  - do not widen into the separate direct-collection-import failure in `test_source_tree_benchmark_anchor_support.py`
  - do not add a new helper module, compatibility alias layer, or source-tree-owner wrapper

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'not combined_suite_no_longer_imports_or_reads_collection_owner_surface_directly'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def (_module_assignment|_module_function_definition|_module_class_definition|_class_method_definition)\\b' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Keep the task bounded to the duplicated generic AST lookup helpers that sit on top of the already-shared parsed-module API in `tests/benchmarks/benchmark_test_support.py`.
- Preserve the current owner-routing split: this task is about removing duplicated lookup plumbing, not moving benchmark-owner assertion logic between suites.

## Notes
- `RBR-1348` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1348|RBR-1349|RBR-1350|RBR-1351' ops/state/current_status.md ops/state/backlog.md` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n '^def (_module_assignment|_module_function_definition|_module_class_definition|_class_method_definition)\\b' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows all six generic AST lookup helpers still split across the two suites even though both already build on `benchmark_test_support._parsed_module_ast(...)`
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'not combined_suite_no_longer_imports_or_reads_collection_owner_surface_directly'` passed with `235 passed, 1 deselected in 1.56s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` was not rerun in this planning pass
  - `bash -lc "! rg -n '^def (_module_assignment|_module_function_definition|_module_class_definition|_class_method_definition)\\b' tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because those duplicated generic lookup helpers still live locally in the two suites, and that failure belongs exactly to this cleanup
