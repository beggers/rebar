## RBR-1414: Move the compiled-pattern `module.compile` owner helper layer onto source-tree support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove one remaining compiled-pattern `module.compile` owner-only helper layer from `tests/benchmarks/benchmark_test_support.py`.
- The compiled-pattern `module.compile` selector/signature/payload-round-trip helpers are now only consumed by `tests/benchmarks/source_tree_benchmark_anchor_support.py`, but they still live in shared benchmark support.
- Move that owner-specific surface onto source-tree support so `benchmark_test_support.py` keeps only reusable shared helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these compiled-pattern `module.compile`-only helpers from `tests/benchmarks/benchmark_test_support.py`:
  - `_compiled_pattern_module_compile_keyword_kwargs_signature`
  - `_module_workflow_compiled_pattern_compile_correctness_case_signature`
  - `_module_workflow_compiled_pattern_compile_workload_signature`
  - `_is_module_workflow_compiled_pattern_compile_workload`
  - `_is_module_workflow_compiled_pattern_compile_success_workload`
  - `_workload_matches_expected_exception`
  - `_module_workflow_compiled_pattern_compile_keyword_correctness_case_signature`
  - `_module_workflow_compiled_pattern_compile_keyword_workload_signature`
  - `_is_module_workflow_compiled_pattern_compile_keyword_workload`
  - `_assert_compiled_pattern_module_compile_contract_payload_round_trip_common`
  - `_assert_compiled_pattern_module_compile_success_payload_round_trip`
  - `_assert_compiled_pattern_module_compile_keyword_payload_round_trip`
- Recreate that helper layer on `tests/benchmarks/source_tree_benchmark_anchor_support.py` with the same behavior.
- Rewire `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE`, `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE`, and the related owner-spec methods on `tests/benchmarks/source_tree_benchmark_anchor_support.py` to call the owner-local helpers instead of `benchmark_test_support._module_workflow_compiled_pattern_compile_*`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the owner-surface assertions, AST checks, and routed-helper assertions treat those compiled-pattern `module.compile` helpers as source-tree-owned rather than shared.
- Update `tests/benchmarks/test_benchmark_test_support.py` so ownership assertions no longer expect those compiled-pattern `module.compile` helpers on `tests/benchmarks/benchmark_test_support.py`.
- Keep genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py`, including:
  - `StandardBenchmarkAnchorContractDefinition`
  - `_contract_source_workloads(...)`
  - `_definition_anchor_expectations(...)`
  - `_workload_case_pair_anchor_expectations(...)`
  - `freeze_signature_value(...)`
  - `compiled_pattern_contract_expected_build_calls(...)`
- Do not widen into collection-replacement cleanup, pattern-boundary cleanup, benchmark manifests, reports, or tracked project-state docs.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1414|RBR-1415|RBR-1416" ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` found no reserved future-id use for `RBR-1414`; the only hit was a historical note inside a done task.
- Candidate selection in this run:
  - `rg -n "_module_workflow_compiled_pattern_compile_|_compiled_pattern_module_compile_keyword_kwargs_signature|_assert_compiled_pattern_module_compile_" tests/benchmarks` showed the live non-test consumers are all in `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still wires `_COMPILED_PATTERN_MODULE_COMPILE_SUCCESS_CONTRACT_ROUTE` and `_COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CONTRACT_ROUTE` through `benchmark_test_support._module_workflow_compiled_pattern_compile_*` helpers, so this is a bounded owner-boundary cleanup rather than a local rename.
  - I stopped after this first viable post-JSON candidate because it removes one entire remaining source-tree-owned helper layer from shared benchmark support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q` passed with `302 passed in 1.20s`.

## Completion Note
- Completed on 2026-03-26.
- Moved the compiled-pattern `module.compile` selector/signature/payload-round-trip helper layer out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Rewired the source-tree contract routes and owner specs to use the owner-local helpers, and updated the focused ownership tests so the shared module no longer claims those helpers.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q` passed with `304 passed in 1.55s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed.
