## RBR-1444: Localize quantified-group trace helper layer onto owner suites

Owner: architecture-implementation
Created: 2026-03-27

## Goal
- Remove the remaining quantified-group compile-trace helper layer from `tests/python/fixture_parity_support.py`, where two owner suites still import shared trace-case builders that only serve their local pattern-trace coverage.
- Keep `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` responsible for their own trace-case helper construction so shared fixture parity support stays focused on genuinely cross-suite fixture and parity behavior.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_fixture_parity_support_contract.py`

## Acceptance Criteria
- Rewrite `tests/python/test_open_ended_quantified_group_parity_suite.py` so it no longer imports or calls `build_compile_case_pattern_trace_cases()` from `tests.python.fixture_parity_support`, and instead defines the trace-case builder(s) it needs locally.
- Rewrite `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py` so it no longer imports or calls `build_pattern_trace_cases()` from `tests.python.fixture_parity_support`, and instead defines the trace-case builder(s) it needs locally.
- Remove `compile_case_trace_prefix()`, `build_pattern_trace_cases()`, and `build_compile_case_pattern_trace_cases()` from `tests/python/fixture_parity_support.py`, along with any imports that only supported that trace-helper layer.
- Tighten `tests/python/test_fixture_parity_support_contract.py` so the shared-support contract asserts those trace helpers stay owner-local and no longer exist on `tests.python.fixture_parity_support`.
- Keep the run bounded to this shared-layer deletion:
  - do not move or rewrite `PatternTraceCase`, direct-bytes follow-on helpers, generated-spec helpers, or published fixture-bundle loaders
  - do not change correctness fixtures, benchmark workloads, harness runtime behavior, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_fixture_parity_support_contract.py -k 'compile_case_trace_prefix or build_compile_case_pattern_trace_cases or build_pattern_trace_cases'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py -k 'trace_cases or pattern_trace'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'trace_cases or pattern_trace'`
- `bash -lc "! rg -n '\\b(compile_case_trace_prefix|build_pattern_trace_cases|build_compile_case_pattern_trace_cases)\\b' tests/python/fixture_parity_support.py"`
- `./.venv/bin/python -m py_compile tests/python/fixture_parity_support.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_fixture_parity_support_contract.py`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1444|RBR-1445|RBR-1446" ops/state/current_status.md ops/state/backlog.md` returned no matches, so `RBR-1444` was available.
- Candidate selection in this run:
  - `rg -n "\\b(build_compile_case_pattern_trace_cases|build_pattern_trace_cases|compile_case_trace_prefix)\\b" tests/python` showed this trace-helper layer is defined only in `tests/python/fixture_parity_support.py`, consumed only by `tests/python/test_open_ended_quantified_group_parity_suite.py` and `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`, and otherwise referenced only by the shared-support contract suite.
  - That makes the trace builders a viable owner-local layer deletion rather than a still-shared fixture/parity abstraction.
  - I rejected `tests/benchmarks/benchmark_test_support.py` as the first fallback because the remaining exports there are still actively shared across benchmark owner suites and manifest-validation coverage, so the next bounded step in that file would have been another local helper trim rather than an entire cross-file layer removal.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_fixture_parity_support_contract.py -k 'compile_case_trace_prefix or build_compile_case_pattern_trace_cases or build_pattern_trace_cases'` passed (`3 passed, 425 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_open_ended_quantified_group_parity_suite.py -k 'trace_cases or pattern_trace'` passed (`7 passed, 3895 deselected`).
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py -k 'trace_cases or pattern_trace'` passed (`1 passed, 1352 deselected`).
  - `bash -lc "! rg -n '\\b(compile_case_trace_prefix|build_pattern_trace_cases|build_compile_case_pattern_trace_cases)\\b' tests/python/fixture_parity_support.py"` is currently red because that shared trace-helper layer still exists and is the target of this task.
