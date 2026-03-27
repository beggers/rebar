## RBR-1433: Localize support-only synthetic benchmark builders onto the support meta-tests

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining synthetic benchmark builder layer from `tests/benchmarks/benchmark_test_support.py` when that layer exists only to support `tests/benchmarks/test_benchmark_test_support.py`.
- `tests/benchmarks/benchmark_test_support.py` still owns a cluster of synthetic manifest/workload helpers plus a module-pattern case builder that are not used by benchmark owner suites or publication/runtime contract suites. The live filesystem check in this run showed those helpers are referenced only from `tests/benchmarks/test_benchmark_test_support.py`, so they do not belong in shared benchmark support anymore.
- Keep `tests/benchmarks/benchmark_test_support.py` focused on genuinely shared benchmark helpers, and let the support meta-tests own the synthetic fixtures they use to probe that shared surface.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Move or inline the support-only synthetic builder layer out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/test_benchmark_test_support.py`, so shared support no longer exports helpers that are consumed only by its own meta-tests:
  - `_synthetic_manifest(...)`
  - `_synthetic_case(...)`
  - `_synthetic_workload(...)`
  - `_synthetic_manifest_loader(...)`
  - `_module_pattern_case(...)`
  - `_synthetic_workload_signature(...)`
  - `_synthetic_workload_is_included(...)`
  - `synthetic_workload(...)`
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it owns those synthetic builders locally instead of routing through `tests.benchmarks.benchmark_test_support`.
- Delete the dead shared-support `_synthetic_case(...)` export instead of preserving it as unused compatibility clutter.
- Keep the run bounded to that ownership cleanup:
  - do not change benchmark manifests, runtime behavior, reports, or tracked project-state files
  - do not move helpers that still have real cross-suite consumers such as live manifest loading, CPython workload execution, or ownership-boundary assertion helpers

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'synthetic_workload or contract_source_workloads or compile_proxy or module_pattern_case or anchored_workload_case_pairs or standard_benchmark_anchor_contract_definition' -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py`
- `bash -lc "! rg -n 'def _synthetic_manifest|def _synthetic_case|def _synthetic_workload|def _synthetic_manifest_loader|def _module_pattern_case|def _synthetic_workload_signature|def _synthetic_workload_is_included|def synthetic_workload' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the checkout was not dirty when sizing the next cleanup.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1433|RBR-1434|RBR-1435" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1433` was available.
- Candidate selection in this run:
  - The first post-JSON probe confirmed that the source-tree standard-benchmark anchor layer had already been localized by completed task `RBR-1432`, so reopening that path would have created duplicate queue churn.
  - The second bounded probe showed that `_synthetic_manifest(...)`, `_synthetic_case(...)`, `_synthetic_workload(...)`, `_synthetic_manifest_loader(...)`, `_module_pattern_case(...)`, `_synthetic_workload_signature(...)`, `_synthetic_workload_is_included(...)`, and `synthetic_workload(...)` are defined in `tests/benchmarks/benchmark_test_support.py` but are referenced only by `tests/benchmarks/test_benchmark_test_support.py`.
  - `bash -lc "! rg -n 'def _synthetic_manifest|def _synthetic_case|def _synthetic_workload|def _synthetic_manifest_loader|def _module_pattern_case|def _synthetic_workload_signature|def _synthetic_workload_is_included|def synthetic_workload' tests/benchmarks/benchmark_test_support.py"` is currently red because those support-only builders still live in shared support; that red state belongs to the exact cleanup this task queues.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'synthetic_workload or contract_source_workloads or compile_proxy or module_pattern_case or anchored_workload_case_pairs or standard_benchmark_anchor_contract_definition' -q` passed with `13 passed, 186 deselected in 0.18s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py` passed.

## Completion
- Moved the synthetic benchmark workload/case builders that were only consumed by `tests/benchmarks/test_benchmark_test_support.py` into that meta-test module and rewired the affected tests to call the local helpers directly.
- Removed the dead shared-support synthetic helper exports from `tests/benchmarks/benchmark_test_support.py`, including the unused `_synthetic_case(...)` export, and updated the ownership assertion that previously pinned `_module_pattern_case(...)` as a shared helper.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_test_support.py -k 'synthetic_workload or contract_source_workloads or compile_proxy or module_pattern_case or anchored_workload_case_pairs or standard_benchmark_anchor_contract_definition' -q`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py`
  - `bash -lc \"! rg -n 'def _synthetic_manifest|def _synthetic_case|def _synthetic_workload|def _synthetic_manifest_loader|def _module_pattern_case|def _synthetic_workload_signature|def _synthetic_workload_is_included|def synthetic_workload' tests/benchmarks/benchmark_test_support.py\"`
