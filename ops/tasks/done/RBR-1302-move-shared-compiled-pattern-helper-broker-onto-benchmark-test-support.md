## RBR-1302: Move shared compiled-pattern helper broker onto benchmark_test_support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Stop using `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` as the owner for generic compiled-pattern module-helper routing, signature, and selector helpers by moving the remaining shared surface onto `tests/benchmarks/benchmark_test_support.py`, so the compiled-pattern helper module is left owning only its owner-specific wrong-text-model specs and standard-definition assembly.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move this shared helper surface off `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` and onto `tests/benchmarks/benchmark_test_support.py` without changing behavior:
  - `_compiled_pattern_module_helper_route`
  - `_run_cpython_compiled_pattern_module_helper_workload`
  - `_module_workflow_compiled_pattern_correctness_case_signature`
  - `_module_workflow_compiled_pattern_workload_signature`
  - `_is_module_workflow_compiled_pattern_wrong_text_model_workload`
  - `_is_module_workflow_compiled_pattern_literal_success_workload`
  - `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload`
  - `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload`
- Update the non-owner import sites so they consume the moved helper surface from `tests/benchmarks/benchmark_test_support.py` instead of `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`. This includes:
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- Move the ownership and identity assertions for the moved helper surface onto `tests/benchmarks/test_benchmark_test_support.py`. After this cleanup, `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` should keep only owner-specific wrong-text-model/spec assertions and direct owner-definition coverage, not shared-helper ownership checks.
- Keep `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` built in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, but have it consume the moved shared helpers from `tests/benchmarks/benchmark_test_support.py` while preserving:
  - the existing definition order;
  - the existing definition object identities exported through `STANDARD_BENCHMARK_DEFINITIONS`; and
  - the current compiled-pattern helper routing, CPython parity execution, success-workload selection, and wrong-text-model selection behavior.
- Remove the moved definitions from `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` instead of leaving compatibility aliases, forwarding re-exports, or duplicate implementations behind.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or compiled_pattern_module_success or compiled_pattern_success_rows or module_workflow_compiled_pattern'`
- `bash -lc "! rg -n -U -P 'from tests\\.benchmarks\\.compiled_pattern_module_helper_benchmark_support import \\([\\s\\S]*?(_compiled_pattern_module_helper_route|_run_cpython_compiled_pattern_module_helper_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_is_module_workflow_compiled_pattern_literal_success_workload|_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|_is_module_workflow_compiled_pattern_verbose_bytes_success_workload)' tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Do not add a new helper broker module or leave a compatibility wrapper behind. The point is to centralize genuinely shared compiled-pattern helper support in `tests/benchmarks/benchmark_test_support.py` and trim cross-file leakage from the owner module.
- Preserve the owner-specific wrong-text-model spec tables, owner definition tuple assembly, and owner-focused support coverage in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.

## Notes
- `RBR-1302` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run;
  - `rg -n "RBR-1302|RBR-1303|RBR-1304" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1302`; and
  - the newest live task before this file was `ops/tasks/done/RBR-1301-move-shared-collection-replacement-classifiers-onto-benchmark-test-support.md`.
- No blocked architecture task existed to reopen or retire first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/dashboard.md` showed no inherited-dirty or refresh/commit anomaly in the latest cycle snapshot.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` still imports `_compiled_pattern_module_helper_route` plus the three compiled-pattern success selectors from `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still imports the compiled-pattern success selectors plus `_module_workflow_compiled_pattern_correctness_case_signature`, `_module_workflow_compiled_pattern_workload_signature`, and `_is_module_workflow_compiled_pattern_wrong_text_model_workload` from that owner module; and
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` still treats part of this shared helper surface as owner-owned instead of support-owned.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or compiled_pattern_module_success or compiled_pattern_success_rows or module_workflow_compiled_pattern'` passed with `97 passed, 150 deselected in 0.86s`;
  - `bash -lc "! rg -n -U -P 'from tests\\.benchmarks\\.compiled_pattern_module_helper_benchmark_support import \\([\\s\\S]*?(_compiled_pattern_module_helper_route|_run_cpython_compiled_pattern_module_helper_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_is_module_workflow_compiled_pattern_literal_success_workload|_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|_is_module_workflow_compiled_pattern_verbose_bytes_success_workload)' tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails because those shared helpers still import from `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, and that failure belongs exactly to this cleanup.

## Completion
- Moved the shared compiled-pattern helper route/runtime/signature/selector surface onto `tests/benchmarks/benchmark_test_support.py`, including the private support it depends on.
- Repointed `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` to import the moved helpers from support while preserving its direct `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` assembly and exported definition identities.
- Repointed `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the moved shared helpers from support.
- Moved shared-helper ownership/import/behavior coverage onto `tests/benchmarks/test_benchmark_test_support.py`; trimmed `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` back to owner-specific wrong-text-model/spec coverage and direct owner-definition checks.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or compiled_pattern_module_success or compiled_pattern_success_rows or module_workflow_compiled_pattern'` -> `99 passed, 151 deselected in 0.89s`.
- Verified with `bash -lc "! rg -n -U -P 'from tests\\.benchmarks\\.compiled_pattern_module_helper_benchmark_support import \\([\\s\\S]*?(_compiled_pattern_module_helper_route|_run_cpython_compiled_pattern_module_helper_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_is_module_workflow_compiled_pattern_literal_success_workload|_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload|_is_module_workflow_compiled_pattern_verbose_bytes_success_workload)' tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed with no matches.
