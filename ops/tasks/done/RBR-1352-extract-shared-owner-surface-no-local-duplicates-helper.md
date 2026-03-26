## RBR-1352: Extract a shared owner-surface no-local-duplicates helper

Status: done
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the duplicated wrong-text-model owner-surface assertion setup from `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` and `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` by moving that repeated "owner module owns these names and the consumer test does not" check onto `tests/benchmarks/benchmark_test_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`

## Acceptance Criteria
- Add one shared helper to `tests/benchmarks/benchmark_test_support.py` for benchmark-owner test modules that need to assert all of the following in one place:
  - a caller test module does not define or assign a listed owner surface locally
  - the listed definition names and assignment names exist on the expected owner module
  - an optional extra owner-owned name can be asserted absent from the caller module while still being present on a second owner module
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` to call that shared helper instead of rebuilding local `expected_definition_names` and `expected_assignment_names` sets inline for `test_collection_replacement_pattern_wrong_text_model_support_surface_is_owner_module_owned_without_local_duplicates`.
- Update `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` to call that shared helper instead of rebuilding local `expected_definition_names` and `expected_assignment_names` sets inline for `test_pattern_boundary_wrong_text_model_support_surface_is_owner_module_owned_without_local_duplicates`.
- Keep the cleanup bounded to this duplicated assertion pattern:
  - do not widen into `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - do not move wrong-text-model owner implementations between owner modules
  - do not add a new helper module or wrapper layer outside `tests/benchmarks/benchmark_test_support.py`
  - do not change benchmark manifests, harness behavior, scorecards, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'owner_module_owned_without_local_duplicates'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'expected_definition_names = \\{|expected_assignment_names = \\{' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py"`

## Constraints
- Prefer one shared helper on `tests/benchmarks/benchmark_test_support.py` over another file-local assertion clone.
- Keep the benchmark-owner surface legible: owner modules should still publish the real wrong-text-model names, and the consumer tests should only check that surface through the shared helper instead of reconstructing the same inspection logic.

## Notes
- Completed 2026-03-26: added `assert_owner_surface_module_owned_without_local_duplicates()` to `tests/benchmarks/benchmark_test_support.py` and rewired the collection-replacement and pattern-boundary wrong-text-model owner-surface tests to use it, including the second-owner-module contract-spec check.
- Verified with `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'owner_module_owned_without_local_duplicates'`, `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, and `bash -lc \"! rg -n 'expected_definition_names = \\{|expected_assignment_names = \\{' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py\"`.
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1352|RBR-1353|RBR-1354|RBR-1355' ops/state/current_status.md ops/state/backlog.md ops/tasks || true` returned only historical mentions inside completed task notes; no reserved frontier entry exists in `ops/state/current_status.md` or `ops/state/backlog.md`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Rule 10 did not apply in this checkout: `.rebar/runtime/dashboard.md` shows no queue-stall anomaly, no inherited-dirty churn, and no ready `feature-implementation` task waiting behind a broken refresh/commit path.
- First candidate probe in this run found no remaining benchmark-test alias assignments of the form `_<NAME> = support.<NAME>` or `_<NAME> = source_tree_support.<NAME>` across `tests/benchmarks/test_*.py`, so this run did not seed another owner-alias cleanup.
- Second candidate probe found one live duplicated assertion pattern across two files:
  - `rg -n 'top_level_module_definition_and_assignment_names\\(sys\\.modules\\[__name__\\]\\)|expected_definition_names = \\{|expected_assignment_names = \\{' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` reports the remaining inline owner-surface inspection blocks
  - both tests currently pass, so the duplication can be removed without waiting on unrelated feature work
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py -k 'owner_module_owned_without_local_duplicates'` passed with `2 passed, 173 deselected in 0.12s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed
  - `bash -lc "! rg -n 'expected_definition_names = \\{|expected_assignment_names = \\{' tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py"` currently fails because both test files still carry those duplicated inline expectation blocks, and that failure belongs exactly to this cleanup
