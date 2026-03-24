## RBR-1241: Collapse compiled-pattern module success support onto owned surfaces

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the mixed `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` layer now that it only brokers two bounded helper families between existing benchmark-support owners plus one dedicated contract test. The collection/replacement compiled-pattern success selectors should live on the collection/replacement anchor owner, the module-boundary compiled-pattern success selectors should live on the compiled-pattern module-helper owner, and the dedicated contract test should keep its owner-spec scaffolding locally instead of routing through a standalone bridge module.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`

## Acceptance Criteria
- Delete the standalone mixed support layer:
  - remove `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`; and
  - update benchmark-test imports so no `tests/benchmarks/*.py` file still imports `compiled_pattern_module_success_benchmark_support`.
- Fold the collection/replacement compiled-pattern success selectors and signatures onto the existing collection/replacement owner in `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - move `_collection_replacement_compiled_pattern_success_correctness_case_signature(...)`;
  - move `_collection_replacement_compiled_pattern_success_workload_args(...)`;
  - move `_collection_replacement_compiled_pattern_success_workload_signature(...)`; and
  - move `_is_collection_replacement_compiled_pattern_success_workload(...)`.
- Fold the module-boundary compiled-pattern success selectors and signatures onto the existing compiled-pattern helper owner in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`:
  - move `_module_workflow_compiled_pattern_correctness_case_signature(...)`;
  - move `_module_workflow_compiled_pattern_workload_args(...)`;
  - move `_module_workflow_compiled_pattern_workload_signature(...)`;
  - move `_is_module_workflow_compiled_pattern_workload(...)`;
  - move `_is_module_workflow_compiled_pattern_literal_success_workload(...)`;
  - move `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(...)`; and
  - move `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload(...)`.
- Rehome the dedicated contract-only scaffolding onto `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` instead of keeping it in a shared support module:
  - move `CompiledPatternModuleSuccessOwnerSpec`;
  - move the two owner-spec constants plus `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`;
  - move `_assert_compiled_pattern_module_success_payload_round_trip(...)`; and
  - move `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`.
- Rehome focused selector/signature coverage onto the existing owner suites instead of leaving it stranded behind the deleted bridge:
  - add direct collection/replacement compiled-pattern success selector/signature assertions to `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`; and
  - add direct module-boundary compiled-pattern success selector/signature assertions to `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`.
- Update the combined benchmark suite to import the moved selectors from their owners directly:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must import the collection/replacement success helpers from `collection_replacement_benchmark_anchor_support.py`; and
  - it must import the module-boundary compiled-pattern success helpers from `compiled_pattern_module_helper_benchmark_support.py`.
- Preserve the current bounded benchmark-contract behavior exactly:
  - the collection/replacement compiled-pattern success rows selected from `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order;
  - the module-boundary compiled-pattern success rows selected from `benchmarks/workloads/module_boundary.py` must stay identical and in the same order;
  - the callback build ordering and callback-call shapes must continue to flow through the existing `_compiled_pattern_module_helper_route(...)` and `compiled_pattern_contract_expected_build_calls(...)` surfaces; and
  - do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! test -e tests/benchmarks/compiled_pattern_module_success_benchmark_support.py"`

## Constraints
- Keep the cleanup structural and bounded to the benchmark support/test layer listed above.
- Prefer moving helper ownership onto the existing owner support modules and the dedicated owner test over creating another shared support layer or moving helpers between benchmark test files.
- Preserve selector rules, workload-id ordering, payload round-trip checks, callback semantics, and exact CPython result assertions.

## Notes
- `RBR-1241` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1241|RBR-1242|RBR-1243|RBR-1244|RBR-1245|RBR-1246|RBR-1247|RBR-1248" ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` is `395` lines and `rg -n "compiled_pattern_module_success_benchmark_support" tests/benchmarks -g '*.py'` matches only `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`;
  - the collection/replacement helpers inside that module already depend on `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`; and
  - the module-boundary helpers inside that module already depend on `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` passed with `111 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed with `108 tests collected`.
  - `bash -lc "! test -e tests/benchmarks/compiled_pattern_module_success_benchmark_support.py"` currently fails because the bridge module still exists, and that failure belongs to the exact cleanup queued here.
  - The broader execution command `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is intentionally not the task acceptance command because `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is already red in the current checkout for unrelated alternation-heavy callable-replacement expectation drift.
