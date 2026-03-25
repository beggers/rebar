## RBR-1305: Move compiled-pattern module-helper surface onto owner support

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern module-helper owner surface from `tests/benchmarks/benchmark_test_support.py` by moving it onto `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, so the generic benchmark support module stops owning helper routing and workload selectors that already belong to the compiled-pattern module-helper owner lane.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` so it directly owns the full compiled-pattern module-helper surface that currently lives in `tests/benchmarks/benchmark_test_support.py`, including these functions:
  - `_compiled_pattern_module_helper_route`
  - `_run_cpython_compiled_pattern_module_helper_workload`
  - `_is_module_workflow_compiled_pattern_wrong_text_model_workload`
  - `_module_workflow_compiled_pattern_correctness_case_signature`
  - `_module_workflow_compiled_pattern_workload_signature`
  - `_is_module_workflow_compiled_pattern_workload`
  - `_is_module_workflow_compiled_pattern_literal_success_workload`
  - `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload`
  - `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload`
- Keep any small private constants or imports those helpers need inside `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` instead of leaving them stranded in `tests/benchmarks/benchmark_test_support.py`, while preserving the current literal-success, bounded-wildcard, verbose-bytes, and wrong-text-model selector semantics for both module-boundary and collection-replacement compiled-pattern helper workflows.
- Update `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` and the compiled-pattern benchmark suites so they import the moved helper surface from `tests.benchmarks.compiled_pattern_module_helper_benchmark_support` rather than from `tests.benchmarks.benchmark_test_support`.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so its compiled-pattern helper imports come from `tests.benchmarks.compiled_pattern_module_helper_benchmark_support`, matching the owner boundary used by the support modules.
- Slim `tests/benchmarks/benchmark_test_support.py` so it no longer defines the nine moved helpers above. Keep only genuinely shared support there; do not add a new compatibility wrapper or a new intermediate support module in this task.
- Update `tests/benchmarks/test_benchmark_test_support.py` so it pins the corrected ownership boundary directly:
  - assert the moved compiled-pattern module-helper helpers are no longer defined in `tests.benchmarks.benchmark_test_support`;
  - assert `tests.benchmarks.compiled_pattern_module_helper_benchmark_support` defines or exports that helper surface; and
  - assert the non-owner suites that still need those helpers import them from `tests.benchmarks.compiled_pattern_module_helper_benchmark_support`, not from the generic support module.
- Keep the existing compiled-pattern module-helper and compiled-pattern module-success behavioral assertions intact. The target is ownership cleanup, not a change to benchmark callback shapes, CPython result materialization, or live workload membership.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or compiled_pattern_module_success or shared_compiled_pattern_helper'`
- `bash -lc "! rg -n '^def (_compiled_pattern_module_helper_route|_run_cpython_compiled_pattern_module_helper_workload|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_workload|_is_module_workflow_compiled_pattern_literal_success_workload|_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|_is_module_workflow_compiled_pattern_verbose_bytes_success_workload)\\(' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep this cleanup structural and bounded to the seven files above. Do not widen it into benchmark workload manifests, harness runtime behavior, scorecard publication, README text, or tracked `ops/state/` prose.
- Reuse `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` as the owner. Do not add another support module, broker layer, or wrapper export just to preserve the old import path.
- Preserve the current compiled-pattern helper callback-call shapes, result materialization rules, selector boundaries, and standard benchmark definition identities.

## Notes
- `RBR-1305` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1305|RBR-1306|RBR-1307|RBR-1308" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1305`.
- No blocked architecture task existed to reopen or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, and no blocked tasks; and
  - the most recent `architecture-implementation` run finished `done`.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/benchmark_test_support.py` still defines the nine-function compiled-pattern module-helper surface listed above at lines `921` through `1148`;
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` currently imports that same surface from `tests.benchmarks.benchmark_test_support` instead of defining it locally; and
  - `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still consume part of that surface through non-owner imports.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or compiled_pattern_module_success or shared_compiled_pattern_helper'` currently fails with one ownership-boundary assertion in `tests/benchmarks/test_benchmark_test_support.py`, and that failure belongs exactly to this cleanup because the generic support test still expects the success suite to import `_compiled_pattern_module_helper_route` from `tests.benchmarks.benchmark_test_support`;
  - `rg -n '^def (_compiled_pattern_module_helper_route|_run_cpython_compiled_pattern_module_helper_workload|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_workload|_is_module_workflow_compiled_pattern_literal_success_workload|_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|_is_module_workflow_compiled_pattern_verbose_bytes_success_workload)\\(' tests/benchmarks/benchmark_test_support.py` currently reports all nine local definitions, and that failure belongs exactly to this cleanup; and
  - `rg -n '^def (_compiled_pattern_module_helper_route|_run_cpython_compiled_pattern_module_helper_workload|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_workload|_is_module_workflow_compiled_pattern_literal_success_workload|_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|_is_module_workflow_compiled_pattern_verbose_bytes_success_workload)\\(' tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` currently returns no matches, confirming the owner module still lacks the moved helper definitions.
