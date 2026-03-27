## RBR-1442: Localize fixture-parity helper passthroughs onto source-tree owner suite

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining shared-support passthrough layer where `tests/benchmarks/benchmark_test_support.py` re-exports fixture-parity helpers only so `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` can reach them through the `benchmark_test_support` alias.
- Keep the combined boundary owner suite responsible for its own fixture-parity imports instead of routing those helper calls through benchmark shared support.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the suite no longer calls `benchmark_test_support.case_pattern`, `benchmark_test_support.module_workflow_positional_args_signature`, or `benchmark_test_support.module_workflow_keyword_kwargs_signature`.
- Remove those three fixture-parity helper imports from `tests/benchmarks/benchmark_test_support.py` once the owner suite uses its existing direct imports instead.
- Tighten `tests/benchmarks/test_benchmark_test_support.py` so the benchmark-support contract asserts those three owner-local helper routes stay out of `benchmark_test_support`.
- Keep the run bounded to this support-layer deletion:
  - do not move `assert_pattern_parity` or `assert_match_result_parity` out of `tests/benchmarks/benchmark_test_support.py`
  - do not broaden the cleanup into `tests/python/fixture_parity_support.py`, benchmark manifests, harness runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree or benchmark_test_support'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'callable_signature or keyword_signature or positional_args_signature or case_pattern'`
- `bash -lc "! rg -n 'benchmark_test_support\\.(case_pattern|module_workflow_positional_args_signature|module_workflow_keyword_kwargs_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1442|RBR-1443|RBR-1444|RBR-1445" ops/state/current_status.md ops/state/backlog.md` returned no reserved future ids, so `RBR-1442` was available.
- Candidate selection in this run:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already imports `case_pattern`, `module_workflow_positional_args_signature`, and `module_workflow_keyword_kwargs_signature` directly from `tests.python.fixture_parity_support`.
  - A live reference scan showed the only remaining uses of `benchmark_test_support.case_pattern`, `benchmark_test_support.module_workflow_positional_args_signature`, and `benchmark_test_support.module_workflow_keyword_kwargs_signature` are the nine call sites inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` already imports `callable_match_group_signature` directly from `tests.python.fixture_parity_support`, so this cleanup can stay bounded to deleting the owner-only passthrough layer instead of reopening broader fixture-parity routing.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree or benchmark_test_support'` passed (`214 passed`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'callable_signature or keyword_signature or positional_args_signature or case_pattern'` passed (`1 passed, 312 deselected`).
  - `bash -lc "! rg -n 'benchmark_test_support\\.(case_pattern|module_workflow_positional_args_signature|module_workflow_keyword_kwargs_signature)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` is currently red because those exact passthrough calls still exist in the owner suite.
  - `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_test_support.py` passed.
