## RBR-1413: Move the pattern-boundary owner surface out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove one remaining pattern-boundary-owned helper layer from `tests/benchmarks/benchmark_test_support.py`.
- The pattern-boundary selector/signature helpers still live in shared benchmark support even though the only owner for that lane is `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`.
- Move that owner-specific surface onto pattern-boundary support so `benchmark_test_support.py` keeps only reusable shared helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete these pattern-boundary-specific helpers from `tests/benchmarks/benchmark_test_support.py`:
  - `_pattern_window_positional_indexlike_correctness_case_signature`
  - `_pattern_window_positional_indexlike_workload_args`
  - `_pattern_window_positional_indexlike_workload_signature`
  - `_is_pattern_window_positional_indexlike_workload`
  - `_pattern_keyword_window_correctness_case_signature`
  - `_pattern_keyword_window_workload_signature`
  - `_is_pattern_keyword_window_workload`
  - `_pattern_bounded_wildcard_correctness_case_signature`
  - `_pattern_bounded_wildcard_workload_signature`
  - `_is_pattern_bounded_wildcard_workload`
  - `_pattern_verbose_regression_correctness_case_signature`
  - `_pattern_verbose_regression_workload_signature`
  - `_is_pattern_verbose_regression_workload`
- Move the related pattern-boundary constants off shared support as well when they are only used by that lane:
  - `_PATTERN_BOUNDED_WILDCARD_WORKLOAD_IDS`
  - `_PATTERN_BOUNDED_WILDCARD_CASE_IDS`
  - `_PATTERN_SEARCH_VERBOSE_REGRESSION_WORKLOAD_IDS`
  - `_PATTERN_VERBOSE_REGRESSION_WORKLOAD_IDS`
  - `_PATTERN_VERBOSE_REGRESSION_CASE_IDS`
  - `_PATTERN_VERBOSE_REGRESSION_PATTERN`
- Recreate that surface on `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` with the same behavior and keep `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` wired to the local owner helpers instead of `benchmark_test_support._pattern_*`.
- Update `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` so its pinned selector/signature assertions call the owner module for this lane instead of routing those names through the shared-support alias.
- Update `tests/benchmarks/test_benchmark_test_support.py` so ownership assertions treat the moved pattern-boundary helpers/constants as owner-owned and no longer expect them on `tests/benchmarks/benchmark_test_support.py`.
- Keep genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py`, including:
  - `StandardBenchmarkAnchorContractDefinition`
  - `freeze_signature_value(...)`
  - `case_pattern(...)`
  - `module_workflow_positional_args_signature(...)`
  - `module_workflow_keyword_kwargs_signature(...)`
  - `synthetic_workload(...)`
- Do not widen into source-tree-owner cleanup, collection-replacement cleanup, benchmark manifests, reports, or tracked project-state docs.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-141[0-9]|RBR-142[0-9]" ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` found no reserved future-id use for `RBR-1413`; the only hits were completed `RBR-1410` through `RBR-1412` task files.
- Candidate selection in this run:
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` already owns `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` plus the wrong-text-model lane, but it still imports the pattern-window, bounded-wildcard, and verbose-regression selectors/signatures from `tests/benchmarks/benchmark_test_support.py`.
  - `tests/benchmarks/test_benchmark_test_support.py` explicitly documents that those helpers still live on shared support, which makes this a concrete cross-file owner-boundary cleanup rather than a local naming tweak.
  - I stopped after this first viable candidate because it removes one entire remaining owner-specific helper layer from shared benchmark support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py -q` passed with `210 passed in 0.69s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed.
