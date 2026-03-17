# RBR-0565: Collapse anchored benchmark parity loops onto one helper

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the repeated anchored-workload CPython result-parity plumbing from the benchmark correctness-anchor tests so one helper in `tests/benchmarks/correctness_anchor_support.py` owns the workload/case lookup and compile-vs-match comparison flow instead of each targeted test file reimplementing it.

## Deliverables
- `tests/benchmarks/correctness_anchor_support.py`
- `tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py`
- `tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`

## Acceptance Criteria
- `tests/benchmarks/correctness_anchor_support.py` grows the smallest shared helper surface needed to own the repeated anchored-result parity loop:
  - add one helper that resolves an expected anchored workload map into the matching filtered `Workload` objects plus published correctness cases, asserting that each expected entry still names exactly one published correctness case and one in-scope workload;
  - add one helper that runs those anchored pairs through the existing CPython dispatch path and applies the current comparison policy: `assert_pattern_parity(...)` for `module.compile`, and `assert_match_result_parity(..., check_regs=True)` for `module.search` and `pattern.fullmatch`;
  - keep the helper surface on top of the existing `published_cases_by_id()`, `run_benchmark_workload_with_cpython()`, and `run_correctness_case_with_cpython()` support path; and
  - do not add another support module, manifest registry, or benchmark-specific adapter layer.
- The targeted anchor-contract tests stop open-coding that same lookup-and-parity loop:
  - `test_counted_repeat_workload_callbacks_match_anchor_case_results()` routes through the shared helper while preserving the current exact-repeat and ranged-repeat parametrization;
  - `NestedGroupBenchmarkCorrectnessAnchorContractTest.test_measured_nested_group_workload_callbacks_match_anchor_case_results()` routes through the shared helper while preserving the current `subTest(workload_id=..., case_id=...)` labeling;
  - `OptionalGroupBenchmarkCorrectnessAnchorContractTest.test_conditional_anchor_row_matches_anchored_cpython_search_result()` routes through the shared helper without changing the single anchored workload it checks.
- Preserve current behavior exactly:
  - keep the current manifest filters, known-gap exclusions, expected anchor-case ids, and benchmark manifest scope unchanged;
  - keep compile workloads compared as pattern parity and search/fullmatch workloads compared as match-result parity with `check_regs=True`;
  - do not refactor grouped-alternation, open-ended, compile-proxy, or signature-builder helpers in this run; and
  - do not change benchmark manifests, correctness fixtures, published reports, README/current-status/backlog prose, or Rust/Python runtime behavior outside this cleanup.
- After the refactor, the three targeted test files no longer directly reference `published_cases_by_id`, `run_benchmark_workload_with_cpython`, `run_correctness_case_with_cpython`, `assert_pattern_parity`, or `assert_match_result_parity`; that direct dependency should live only in `tests/benchmarks/correctness_anchor_support.py` for this cleanup.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`
  - `rg -n "published_cases_by_id|run_benchmark_workload_with_cpython|run_correctness_case_with_cpython|assert_pattern_parity|assert_match_result_parity" tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup limited to the existing benchmark correctness-anchor support layer and the three targeted test files. Do not broaden it into grouped-alternation/open-ended anchor coverage, selector redesign, manifest-shape cleanup, or feature/parity work.
- Prefer extending `tests/benchmarks/correctness_anchor_support.py` over adding another helper file or pushing more assertion logic into the individual tests.
- Preserve the existing test granularity and diagnostics, especially the nested-group subtest labels and the counted-repeat parametrized coverage.

## Notes
- `RBR-0564` is already filed as the active feature task, and `ops/state/backlog.md` plus `ops/state/current_status.md` do not reserve any `RBR-0565+` ids, so `RBR-0565` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - the last cycle finished both `architecture-implementation` and `feature-implementation` tasks as `done`, so there is no inherited-dirty or post-task refresh/commit stall to yield to.
- JSON burn-down is complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` HEAD `7b30728c121b335ff3b4c4f94e7ceb9750228c11` matches `git rev-parse HEAD`;
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate anchored-parity surface is concrete in the current checkout:
  - `rg -n "published_cases_by_id|run_benchmark_workload_with_cpython|run_correctness_case_with_cpython|assert_pattern_parity|assert_match_result_parity" tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py` currently returns 28 matches across the three targeted files; and
  - those matches are the repeated workload/case lookup plus CPython result-parity loop that already sits adjacent to shared low-level anchor helpers in `tests/benchmarks/correctness_anchor_support.py`.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/benchmarks/test_counted_repeat_benchmark_correctness_anchor_contract.py tests/benchmarks/test_nested_group_benchmark_correctness_anchor_contract.py tests/benchmarks/test_optional_group_benchmark_correctness_anchor_contract.py` passes (`15 passed, 6 subtests passed in 0.08s`).
